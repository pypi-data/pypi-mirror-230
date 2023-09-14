from typing import Optional, Any, Tuple
from enum import Enum
import json
import os
from datetime import datetime
from contextlib import contextmanager
from kazoo.client import KazooClient

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

class ZKError(Enum):
    OK = 1                          # Operation completed successfully
    PIPELINE_ALREADY_REGISTERED = 2
    PIPELINE_NOT_REGISTERED     = 3
    PIPELINE_IS_RUNNING         = 4
    PIPELINE_HAS_EXECUTORS      = 5
    EXECUTOR_ALREADY_EXIST      = 6
    EXECUTOR_NOT_FOUND          = 7

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

    def register_pipeline(
        self, 
        pipeline_id:str, 
        pipeline_namespace_name:str, 
        pipeline_image_name:str, 
        pipeline_module_name:str, 
        pipeline_info:dict,
        k8s_state:dict
    ) -> ZKError:
        """
        Register a pipeline
        """
        pipeline_path = f"/pipelines/{pipeline_id}"
        if self.exists(pipeline_path):
            return ZKError.PIPELINE_ALREADY_REGISTERED
        
        self.ensure_path(pipeline_path)
        self.create_json(f"{pipeline_path}/info", pipeline_info)
        self.create_str(f"{pipeline_path}/module", pipeline_module_name)
        self.create_str(f"{pipeline_path}/namespace_name", pipeline_namespace_name)
        self.create_str(f"{pipeline_path}/image_name", pipeline_image_name)
        self.create_boolean(f"{pipeline_path}/is_running", False)
        self.create_json(f"{pipeline_path}/k8s_state", k8s_state)
        return ZKError.OK

    def unregister_pipeline(self, pipeline_id:str) -> ZKError:
        """
        Unregister a pipeline
        """
        pipeline_path = f"/pipelines/{pipeline_id}"
        if not self.exists(pipeline_path):
            return ZKError.PIPELINE_NOT_REGISTERED
        
        # You can only unregister a pipeline if it is not running
        if self.get_boolean(f"{pipeline_path}/is_running"):
            return ZKError.PIPELINE_IS_RUNNING

        executors_path = f"{pipeline_path}/executors"
        if self.exists(executors_path) and len(self.get_children(executors_path)) > 0:
            return ZKError.PIPELINE_HAS_EXECUTORS
        
        self.delete(pipeline_path, recursive=True)
        return ZKError.OK

    def get_pipelines(self):
        """
        Get information for all pipelines
        """
        pipelines = []
        for pipeline_id in self.get_children("/pipelines"):
            status, pipeline = self.get_pipeline(pipeline_id)
            assert status == ZKError.OK
            assert pipeline is not None
            pipelines.append(pipeline)
        return pipelines

    def get_executor(self, pipeline_id:str, executor_id:str) -> Tuple[ZKError, Any]:
        """
        Get information for an executor
        """
        executor_path = f"/pipelines/{pipeline_id}/executors/{executor_id}"
        if not self.exists(executor_path):
            return ZKError.EXECUTOR_NOT_FOUND, None
        
        executor_info = self.get_json(f"{executor_path}/info")
        executor_info['id'] = executor_id
        return ZKError.OK, {"info": executor_info}

    def get_pipeline(self, pipeline_id:str) -> Tuple[ZKError, Any]:
        """
        Get information for a pipeline
        """
        pipeline_path = f"/pipelines/{pipeline_id}"
        if not self.exists(pipeline_path):
            return ZKError.PIPELINE_NOT_REGISTERED, None

        pipeline_info   = self.get_json(f"{pipeline_path}/info")
        module          = self.get_str(f"{pipeline_path}/module")
        namespace_name  = self.get_str(f"{pipeline_path}/namespace_name")
        image_name      = self.get_str(f"{pipeline_path}/image_name")
        is_running      = self.get_boolean(f"{pipeline_path}/is_running")
        k8s_state       = self.get_json(f"{pipeline_path}/k8s_state")

        executor_ids_path = f"/pipelines/{pipeline_id}/executors"
        executors = []
        if self.exists(executor_ids_path):
            for executor_id in self.get_children(executor_ids_path):
                error, executor = self.get_executor(pipeline_id, executor_id)
                assert error == ZKError.OK
                assert executor is not None
                executors.append(executor)
        
        return ZKError.OK, {
            "info"          : pipeline_info,
            "module"        : module,
            "image_name"    : image_name,
            "namespace_name": namespace_name,
            "is_running"    : is_running,
            "k8s_state"     : k8s_state,
            "executors"     : executors
        }


    def register_executor(
        self, 
        pipeline_id:str, 
        executor_id:str, 
        generator_id: Optional[str]
    ) ->ZKError:
        """
        Register an executor
        """
        if not self.exists(f"/pipelines/{pipeline_id}"):
            return ZKError.PIPELINE_NOT_REGISTERED
    
        executors_path = f"/pipelines/{pipeline_id}/executors"
        self.ensure_path(executors_path)

        executor_path = f"{executors_path}/{executor_id}"
        if self.exists(executor_path):
            return ZKError.EXECUTOR_ALREADY_EXIST
        
        self.ensure_path(executor_path)

        executor_info = {
            "start_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "pid": os.getpid(),
            "generator_id": generator_id
        }
        self.create_json(f"{executor_path}/info", executor_info)
        return ZKError.OK

     
    def unregister_executor(self, pipeline_id:str, executor_id:str) -> ZKError:
        """
        Unregister an executor
        """
        executor_path = f"/pipelines/{pipeline_id}/executors/{executor_id}"
        if not self.exists(executor_path):
            return ZKError.EXECUTOR_NOT_FOUND
        self.delete(executor_path, recursive=True)
        return ZKError.OK

    def set_pipeline_is_running(self, pipeline_id:str, *, is_running:bool) -> ZKError:
        pipeline_path = f"/pipelines/{pipeline_id}"
        if not self.exists(pipeline_path):
            return ZKError.PIPELINE_NOT_REGISTERED
        self.set_boolean(f"{pipeline_path}/is_running", is_running)
        return ZKError.OK
