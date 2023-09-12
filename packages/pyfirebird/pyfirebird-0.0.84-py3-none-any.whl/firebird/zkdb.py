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
    
    def register_pipeline(
        self, 
        pipeline_id:str, 
        pipeline_namespace_name:str, 
        pipeline_image_name:str, 
        pipeline_module_name:str, 
        pipeline_info:str
    ) -> ZKError:
        """
        Register a pipeline
        """
        pipeline_path = f"/pipelines/{pipeline_id}"
        if self.zk.exists(pipeline_path):
            return ZKError.PIPELINE_ALREADY_REGISTERED
        
        self.zk.ensure_path(pipeline_path)
        self.zk.create(f"{pipeline_path}/info", json.dumps(pipeline_info).encode("utf-8"))
        self.zk.create(f"{pipeline_path}/module", pipeline_module_name.encode("utf-8"))
        self.zk.create(f"{pipeline_path}/namespace_name", pipeline_namespace_name.encode("utf-8"))
        self.zk.create(f"{pipeline_path}/image_name", pipeline_image_name.encode("utf-8"))
        self.zk.create(f"{pipeline_path}/is_running", b'0')
        return ZKError.OK

    def unregister_pipeline(self, pipeline_id:str) -> ZKError:
        """
        Unregister a pipeline
        """
        pipeline_path = f"/pipelines/{pipeline_id}"
        if not self.zk.exists(pipeline_path):
            return ZKError.PIPELINE_NOT_REGISTERED
        
        # You can only unregister a pipeline if it is not running
        value, version = self.zk.get(f"{pipeline_path}/is_running")
        if value != b'0':
            return ZKError.PIPELINE_IS_RUNNING

        executors_path = f"{pipeline_path}/executors"
        if self.zk.exists(executors_path) and len(self.zk.get_children(executors_path)) > 0:
            return ZKError.PIPELINE_HAS_EXECUTORS
        
        self.zk.delete(pipeline_path, recursive=True)
        return ZKError.OK

    def get_pipelines(self):
        """
        Get information for all pipelines
        """
        pipelines = []
        for pipeline_id in self.zk.get_children("/pipelines"):
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
        if not self.zk.exists(executor_path):
            return ZKError.EXECUTOR_NOT_FOUND, None
        v, _ = self.zk.get(f"{executor_path}/info")
        executor_info = json.loads(v.decode("utf-8"))
        executor_info['id'] = executor_id
        return ZKError.OK, {"info": executor_info}

    def get_pipeline(self, pipeline_id:str) -> Tuple[ZKError, Any]:
        """
        Get information for a pipeline
        """
        pipeline_path = f"/pipelines/{pipeline_id}"
        if not self.zk.exists(pipeline_path):
            return ZKError.PIPELINE_NOT_REGISTERED, None

        value, _ = self.zk.get(f"{pipeline_path}/info")
        pipeline_info = json.loads(value.decode("utf-8"))
        value, _ = self.zk.get(f"{pipeline_path}/module")
        module = value.decode("utf-8")
        value, _ = self.zk.get(f"{pipeline_path}/namespace_name")
        namespace_name = value.decode("utf-8")
        value, _ = self.zk.get(f"{pipeline_path}/image_name")
        image_name = value.decode("utf-8")
        value, _ = self.zk.get(f"{pipeline_path}/is_running")
        is_running = value == b'1'

        executor_ids_path = f"/pipelines/{pipeline_id}/executors"
        executors = []
        if self.zk.exists(executor_ids_path):
            for executor_id in self.zk.get_children(executor_ids_path):
                error, executor = self.get_executor(pipeline_id, executor_id)
                assert error == ZKError.OK
                assert executor is not None
                executors.append(executor)
        
        return ZKError.OK, {
            "info": pipeline_info,
            "module": module,
            "image_name": image_name,
            "namespace_name": namespace_name,
            "is_running": is_running,
            "executors": executors
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
        if not self.zk.exists(f"/pipelines/{pipeline_id}"):
            return ZKError.PIPELINE_NOT_REGISTERED
    
        executors_path = f"/pipelines/{pipeline_id}/executors"
        self.zk.ensure_path(executors_path)

        executor_path = f"{executors_path}/{executor_id}"
        if self.zk.exists(executor_path):
            return ZKError.EXECUTOR_ALREADY_EXIST
        
        self.zk.ensure_path(executor_path)

        executor_info = {
            "start_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "pid": os.getpid(),
            "generator_id": generator_id
        }
        self.zk.create(f"{executor_path}/info", json.dumps(executor_info).encode("utf-8"))
        return ZKError.OK

     
    def unregister_executor(self, pipeline_id:str, executor_id:str) -> ZKError:
        """
        Unregister an executor
        """
        executor_path = f"/pipelines/{pipeline_id}/executors/{executor_id}"
        if not self.zk.exists(executor_path):
            return ZKError.EXECUTOR_NOT_FOUND
        self.zk.delete(executor_path, recursive=True)
        return ZKError.OK

    def set_pipeline_is_running(self, pipeline_id:str, is_running:bool) -> ZKError:
        pipeline_path = f"/pipelines/{pipeline_id}"
        if not self.zk.exists(pipeline_path):
            return ZKError.PIPELINE_NOT_REGISTERED
        value, _ = self.zk.get(f"{pipeline_path}/is_running")
        target_value = b'1' if is_running else b'0'
        if value != target_value:
            self.zk.set(f"{pipeline_path}/is_running", target_value)
        return ZKError.OK
