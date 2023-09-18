from typing import Optional, Any, Tuple, List
from enum import Enum
import json
import os
from datetime import datetime
from contextlib import contextmanager
from kazoo.client import KazooClient
from firebird.base import PipelineRegistry, Executor, PipelineInfo, K8SState

@contextmanager
def zkdb(**kwargs):
    zk = KazooClient(**kwargs)
    db = ZKDatabase(zk)
    zk.start()
    try:
        zk.ensure_path("/pipelines")
        zk.ensure_path("/firebird-global-lock")
        # TODO: Monolithic lock is not ideal, only for MVP
        with zk.Lock("/firebird-global-lock", "zkdb"):
            yield db
    finally:
        zk.stop()
        zk.close()

class ZKDBException(Exception):
    pass

class ZKDBInvalidState(ZKDBException): # possible data corruption
    pass

class ZKDBBadArgument(ZKDBException): # invalid operation
    pass

class ZKDatabase:
    """
    Manage zookeeper database
    """
    def __init__(self, zk):
        self.zk = zk

    def create_str(self, path:str, value:str):
        self.zk.create(path, value.encode("utf-8"))

    def create_json(self, path:str, value:dict):
        self.zk.create(path, json.dumps(value).encode("utf-8"))

    def create_boolean(self, path:str, value:bool):
        self.zk.create(path, b'1' if value else b'0')

    def set_str(self, path:str, value:str):
        self.zk.set(path, value.encode("utf-8"))

    def set_boolean(self, path:str, value:bool):
        self.zk.set(path, b'1' if value else b'0')

    def set_json(self, path:str, value:dict):
        self.zk.set(path, json.dumps(value).encode("utf-8"))

    def get_str(self, path:str):
        value, _ = self.zk.get(path)
        return value.decode("utf-8")

    def get_json(self, path:str):
        value, _ = self.zk.get(path)
        return json.loads(value.decode("utf-8"))

    def get_boolean(self, path:str):
        value, _ = self.zk.get(path)
        return value != b'0'

    def ensure_path(self, path):
        return self.zk.ensure_path(path)
    
    def exists(self, path:str):
        return self.zk.exists(path)
    
    def get_children(self, path:str):
        return self.zk.get_children(path)
    
    def delete(self, path:str, *, recursive:bool):
        return self.zk.delete(path, recursive=recursive)

    def register_pipeline(self, pipeline_registry: PipelineRegistry):
        """
        Register a pipeline
        """
        pipeline_info = pipeline_registry.pipeline_info
        pipeline_path = f"/pipelines/{pipeline_info.id}"
        if self.exists(pipeline_path):
            raise ZKDBBadArgument("Pipeliine already registered!")
        
        self.ensure_path(pipeline_path)
        self.create_json(f"{pipeline_path}/info", pipeline_info.to_json())
        self.create_str(f"{pipeline_path}/module", pipeline_registry.module)
        self.create_str(f"{pipeline_path}/namespace_name", pipeline_registry.namespace_name)
        self.create_str(f"{pipeline_path}/image_name", pipeline_registry.image_name)
        self.create_boolean(f"{pipeline_path}/is_running", False)
        self.create_json(f"{pipeline_path}/k8s_state", pipeline_registry.k8s_state.to_json())


    def unregister_pipeline(self, pipeline_id:str):
        """
        Unregister a pipeline
        """
        pipeline_path = f"/pipelines/{pipeline_id}"
        if not self.exists(pipeline_path):
            raise ZKDBBadArgument("Pipeliine not yet registered!")
        
        # You can only unregister a pipeline if it is not running
        if self.get_boolean(f"{pipeline_path}/is_running"):
            raise ZKDBBadArgument("Cannot unregister a pipeline that is currently running!")

        executors_path = f"{pipeline_path}/executors"
        if self.exists(executors_path) and len(self.get_children(executors_path)) > 0:
            raise ZKDBBadArgument("Cannot unregister a pipeline that has executors!")
        
        self.delete(pipeline_path, recursive=True)

    def get_pipelines(self) -> List[PipelineRegistry]:
        """
        Get information for all pipelines
        """
        pipelines = []
        for pipeline_id in self.get_children("/pipelines"):
            pipeline = self.get_pipeline(pipeline_id)
            pipelines.append(pipeline)
        return pipelines

    def get_executor(self, pipeline_id:str, executor_id:str) -> Executor:
        """
        Get information for an executor
        """
        executor_path = f"/pipelines/{pipeline_id}/executors/{executor_id}"
        if not self.exists(executor_path):
            raise ZKDBBadArgument("Executor not found!")
        
        return Executor.from_json(self.get_json(f"{executor_path}/info"))

    def get_pipeline(self, pipeline_id:str) -> PipelineRegistry:
        """
        Get information for a pipeline
        """
        pipeline_path = f"/pipelines/{pipeline_id}"
        if not self.exists(pipeline_path):
            raise ZKDBBadArgument("Pipeline not registered!")

        pipeline_info   = PipelineInfo.from_json(self.get_json(f"{pipeline_path}/info"))
        module          = self.get_str(f"{pipeline_path}/module")
        namespace_name  = self.get_str(f"{pipeline_path}/namespace_name")
        image_name      = self.get_str(f"{pipeline_path}/image_name")
        is_running      = self.get_boolean(f"{pipeline_path}/is_running")
        k8s_state       = K8SState.from_json(self.get_json(f"{pipeline_path}/k8s_state"))

        executor_ids_path = f"/pipelines/{pipeline_id}/executors"
        executors = []
        if self.exists(executor_ids_path):
            for executor_id in self.get_children(executor_ids_path):
                executor = self.get_executor(pipeline_id, executor_id)
                executors.append(executor)
        
        return PipelineRegistry(
            pipeline_info=pipeline_info,
            module=module,
            namespace_name=namespace_name,
            image_name=image_name,
            is_running=is_running,
            k8s_state=k8s_state,
            executors=executors
        )

    def register_executor(self, pipeline_id:str, executor_id:str, generator_id: Optional[str]):
        """
        Register an executor
        """
        if not self.exists(f"/pipelines/{pipeline_id}"):
            raise ZKDBBadArgument("Pipeline not registered!")
    
        executors_path = f"/pipelines/{pipeline_id}/executors"
        self.ensure_path(executors_path)

        executor_path = f"{executors_path}/{executor_id}"
        if self.exists(executor_path):
            raise ZKDBBadArgument("Executor already registered!")
        
        self.ensure_path(executor_path)

        executor = Executor(id=executor_id, start_time=datetime.utcnow(), pid=os.getpid(), generator_id=generator_id)
        self.create_json(f"{executor_path}/info", executor.to_json())

     
    def unregister_executor(self, pipeline_id:str, executor_id:str):
        """
        Unregister an executor
        """
        executor_path = f"/pipelines/{pipeline_id}/executors/{executor_id}"
        if not self.exists(executor_path):
            raise ZKDBBadArgument("Executor not found!")
        self.delete(executor_path, recursive=True)

    def set_pipeline_is_running(self, pipeline_id:str, *, is_running:bool):
        pipeline_path = f"/pipelines/{pipeline_id}"
        if not self.exists(pipeline_path):
            raise ZKDBBadArgument("Pipeline not registered")
        self.set_boolean(f"{pipeline_path}/is_running", is_running)
