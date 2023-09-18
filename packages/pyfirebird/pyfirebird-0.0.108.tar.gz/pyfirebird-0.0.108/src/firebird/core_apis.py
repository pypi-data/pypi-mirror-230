from typing import Optional, List
import importlib

import uuid

from firebird import zkdb
from firebird.libs.k8 import K8Accessor
from firebird.rabbitmq import get_connection, RabbitMQ

from firebird.base import K8SState, Pipeline, PipelineRegistry, PortType

class CoreAPIException(Exception):
    pass

class CoreAPIInvalidArguments(CoreAPIException):
    pass

class CoreAPIs:
    k8_accessor: K8Accessor
    zk_config: dict
    rabbitmq_config: Optional[dict]

    def __init__(self, *, zk_config:dict, k8_accessor:K8Accessor, rabbitmq_config:Optional[dict]=None):
        self.zk_config = zk_config
        self.k8_accessor = k8_accessor
        self.rabbitmq_config = rabbitmq_config
    
    def list_pipelines(self) -> List[PipelineRegistry]:
        with zkdb(**self.zk_config) as db:
            return db.get_pipelines()

    def get_pipeline(self, id:str) -> PipelineRegistry:
        with zkdb(**self.zk_config) as db:
            return db.get_pipeline(id)


    def start_pipeline(self, id:str, replicas:int=1) -> None:
        """Start a pipeline

        Args:
            id (str): pipeline ID
        """
        with zkdb(**self.zk_config) as db:
            pipeline_registry = db.get_pipeline(id)

            if pipeline_registry.is_running:
                raise CoreAPIInvalidArguments(f"Pipeline(id={id}) is already running!")

            self.k8_accessor.apply(
                template_name="pipeline.yaml",
                context={
                    "k8s_state": pipeline_registry.k8s_state.to_json(),
                    "pipeline_namespace_name": pipeline_registry.namespace_name,
                    "pipeline_image_name": pipeline_registry.image_name,
                    "pipeline_id": id,
                    "replicas": replicas,
                    "generator_ids": [node.id for node in pipeline_registry.pipeline_info.get_generators()]
                }
            )
            db.set_pipeline_is_running(id, is_running=True)

    def stop_pipeline(self, id:str) -> None:
        """Stop a pipeline

        Args:
            id (str): pipeline ID
        """
        with zkdb(**self.zk_config) as db:
            pipeline_registry = db.get_pipeline(id)

            if not pipeline_registry.is_running:
                raise CoreAPIInvalidArguments(f"Pipeline(id={id}) is already stopped!")

            for _, statefulset_name in pipeline_registry.k8s_state.generators.items():
                self.k8_accessor.delete_statefulset(
                    namespace=pipeline_registry.namespace_name, 
                    name=statefulset_name
                )

            self.k8_accessor.delete_deployment(
                namespace=pipeline_registry.namespace_name,
                name=pipeline_registry.k8s_state.deployment_name
            )
            db.set_pipeline_is_running(id, is_running=False)

    def register_pipeline(
        self, 
        pipeline_namespace_name:str, 
        pipeline_image_name:str, 
        pipeline_module_name:str
    ) -> None:
        """Register a pipeline

        Args:
            pipeline_namespace_name (str): Namespace name of the pipeline
            pipeline_image_name (str): docker image name of the pipeline
            pipeline_module_name (str): python module name of the pipeline
        """
        pipeline:Pipeline = importlib.import_module(pipeline_module_name).get_pipeline(None)
        pipeline_info = pipeline.get_info()

        # we will assign k8s statefulset name and deployment name, we do not want to use
        # pipeline name and generator id as name since k8s's name has limitation
        # only 63 chars and no upper case characters
        k8s_state = K8SState(
            deployment_name=str(uuid.uuid4()),
            generators={}
        )
        for node in pipeline_info.get_generators():
            k8s_state.generators[node.id] = str(uuid.uuid4())

        mq = RabbitMQ(
            connection = get_connection(**self.rabbitmq_config),
            topic = pipeline.id
        )
        # create rabbitmq topic, etc
        mq.initialize()

        with zkdb(**self.zk_config) as db:
            pipeline_registry = PipelineRegistry(
                pipeline_info = pipeline_info,
                module=pipeline_module_name,
                namespace_name=pipeline_namespace_name,
                image_name=pipeline_image_name,
                is_running=False,
                k8s_state=k8s_state
            )
            db.register_pipeline(pipeline_registry)

    def unregister_pipeline(self, id: str) -> None:
        """Unregister a pipeline

        Args:
            id (str): id of the pipeline to be unregisterred
        """
        with zkdb(**self.zk_config) as db:
            db.unregister_pipeline(id)

        mq = RabbitMQ(
            connection = get_connection(**self.rabbitmq_config),
            topic = id
        )
        # delete queues
        mq.delete_queues()
