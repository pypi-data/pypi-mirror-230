import os
from typing import Optional
import tempfile
import importlib
import graphviz
import xml.dom.minidom

from firebird import zkdb, ZKError
from firebird.libs.k8 import K8Accessor
from firebird.rabbitmq import get_connection, RabbitMQ

class CoreAPIException(Exception):
    pass

class CoreAPIInvalidArguments(CoreAPIException):
    pass

class CoreAPIFailed(CoreAPIException):
    pass

def get_generator_ids(pipeline):
    generator_ids = []
    for node in pipeline["info"]["nodes"]:
        input_port_count = 0
        for port in node["ports"]:
            if port["type"] == "INPUT": # hack, better use PortType enum
                input_port_count += 1
                break
        if input_port_count == 0:
            generator_ids.append(node["id"])
    return generator_ids

class CoreAPIs:
    k8_accessor: K8Accessor
    zk_config: dict
    rabbitmq_config: Optional[dict]

    def __init__(self, *, zk_config:dict, k8_accessor:K8Accessor, rabbitmq_config:Optional[dict]=None):
        self.zk_config = zk_config
        self.k8_accessor = k8_accessor
        self.rabbitmq_config = rabbitmq_config
    
    def list_pipelines(self):
        with zkdb(**self.zk_config) as db:
            pipelines = db.get_pipelines()
        return {"pipelines": pipelines}

    def get_pipeline(self, id:str):
        with zkdb(**self.zk_config) as db:
            error, pipeline = db.get_pipeline(id)
            if error != ZKError.OK:
                raise CoreAPIInvalidArguments(f"Unable to get pipeline(id={id}), error is {error}")

        filename = None
        svg_filename = None
        with tempfile.NamedTemporaryFile(prefix="firebird-svg-", delete=False) as f:
            filename = f.name
            svg_filename = f"{filename}.svg"

        svgs = []
        for rankdir in ["LR", "TB"]:
            try:
                edges = set()
                g = graphviz.Digraph(format="svg")
                g.attr(bgcolor="transparent")
                g.attr(rankdir=rankdir)
                for node in pipeline["info"]["nodes"]:
                    g.node(node['id'], node['title'], shape="box", href="#", style="filled", fillcolor="green")

                    for port in node["ports"]:
                        if port["type"] == "OUTPUT":
                            for connected_port in port["connected_ports"]:
                                next_node_id, _ = connected_port.split(":")
                                edges.add((node["id"], next_node_id))
                for src_node_id, next_node_id in edges:
                    g.edge(src_node_id, next_node_id)
                g.render(filename=filename)

                doc = xml.dom.minidom.parse(svg_filename)
                svg = doc.documentElement.toxml()
                svgs.append(svg)
            finally:
                for fn in [filename, svg_filename]:
                    if os.path.isfile(fn):
                        os.remove(fn)

        return {
            "pipeline": pipeline,
            "svg_lr": svgs[0],
            "svg_tb": svgs[1],
        }


    def start_pipeline(self, id:str, replicas:int=1) -> None:
        """Start a pipeline

        Args:
            id (str): pipeline ID
        """
        with zkdb(**self.zk_config) as db:
            error, pipeline = db.get_pipeline(id)

            if error != ZKError.OK:
                raise CoreAPIInvalidArguments(f"Unable to get pipeline(id={id}), error is {error}")

            if pipeline['is_running']:
                raise CoreAPIInvalidArguments(f"Pipeline(id={id}) is already running!")
        
            self.k8_accessor.apply(
                template_name="pipeline.yaml",
                context={
                    "pipeline_namespace_name": pipeline["namespace_name"],
                    "pipeline_image_name": pipeline["image_name"],
                    "pipeline_id": id,
                    "replicas": replicas,
                    "generator_ids": get_generator_ids(pipeline)
                }
            )
            error = db.set_pipeline_is_running(id, True)
            if error != ZKError.OK:
                raise CoreAPIFailed(f"Unable to change pipeline(id={id}) to running status, error is {error}")

    def stop_pipeline(self, id:str) -> None:
        """Stop a pipeline

        Args:
            id (str): pipeline ID
        """
        with zkdb(**self.zk_config) as db:
            error, pipeline = db.get_pipeline(id)

            if error != ZKError.OK:
                raise CoreAPIInvalidArguments(f"Unable to get pipeline(id={id}), error is {error}")

            if not pipeline['is_running']:
                raise CoreAPIInvalidArguments(f"Pipeline(id={id}) is not running!")

            for generator_id in get_generator_ids(pipeline):
                name = f"firebird-pipeline--{id}--{generator_id}"
                self.k8_accessor.delete_statefulset(namespace=pipeline["namespace_name"], name=name)

            name = f"firebird-pipeline--{id}"
            self.k8_accessor.delete_deployment(namespace=pipeline["namespace_name"], name=name)

            error = db.set_pipeline_is_running(id, False)
            if error != ZKError.OK:
                raise CoreAPIFailed(f"Unable to change pipeline to stopped status, error is {error}")

    def register_pipeline(self, pipeline_namespace_name:str, pipeline_image_name:str, pipeline_module_name:str) -> None:
        """Register a pipeline

        Args:
            pipeline_namespace_name (str): Namespace name of the pipeline
            pipeline_image_name (str): docker image name of the pipeline
            pipeline_module_name (str): python module name of the pipeline
        """
        pipeline = importlib.import_module(pipeline_module_name).get_pipeline(None)
        pipeline_info = pipeline.to_json()

        mq = RabbitMQ(
            connection = get_connection(**self.rabbitmq_config),
            topic = pipeline.id
        )
        # create rabbitmq topic, etc
        mq.initialize()

        with zkdb(**self.zk_config) as db:
            error = db.register_pipeline(
                pipeline.id, 
                pipeline_namespace_name, 
                pipeline_image_name, 
                pipeline_module_name, 
                pipeline_info
            )
            if error != ZKError.OK:
                raise CoreAPIFailed(f"register pipeline failed, error is: {error}")

    def unregister_pipeline(self, id: str) -> None:
        """Unregister a pipeline

        Args:
            id (str): id of the pipeline to be unregisterred
        """
        with zkdb(**self.zk_config) as db:
            error = db.unregister_pipeline(id)
            if error != ZKError.OK:
                raise CoreAPIFailed(f"unregister pipeline failed, error is: {error}")

