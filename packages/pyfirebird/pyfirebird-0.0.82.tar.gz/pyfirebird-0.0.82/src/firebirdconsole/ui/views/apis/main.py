import logging

from .api_base import RESTAPIBase, ServerInternalError

import os
from django.http  import HttpRequest
from django.conf import settings
from firebird import zkdb, ZKError
import tempfile
import xml.dom.minidom
import graphviz
from django.core.exceptions import BadRequest
from firebird.libs.k8 import K8ACCESSOR

logger = logging.getLogger(__name__)


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

class PipelinesAPI(RESTAPIBase):
    def list(self, request:HttpRequest, **kwargs):
        with zkdb(**settings.FIREBIRD_CONFIG['zookeeper']) as db:
            pipelines = db.get_pipelines()
        return {"pipelines": pipelines}

    def get(self, request:HttpRequest, id:str, **kwargs):
        with zkdb(**settings.FIREBIRD_CONFIG['zookeeper']) as db:
            error, pipeline = db.get_pipeline(id)
            if error != ZKError.OK:
                raise BadRequest(f"Cannot get pipeline {id}")

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

    def start(self, request:HttpRequest, id:str, **kwargs):
        with zkdb(**settings.FIREBIRD_CONFIG['zookeeper']) as db:
            error, pipeline = db.get_pipeline(id)

            if error != ZKError.OK:
                raise BadRequest(f"Unable to get pipeline, error is {error}")

            if pipeline['is_running']:
                raise BadRequest(f"Pipeline is already running!")
        
            K8ACCESSOR.apply(
                template_name="pipeline.yaml",
                context={
                    "pipeline_namespace_name": pipeline["namespace_name"],
                    "pipeline_image_name": pipeline["image_name"],
                    "pipeline_id": id,
                    "replicas": 1,
                    "generator_ids": get_generator_ids(pipeline)
                }
            )
            error = db.set_pipeline_is_running(id, True)
            if error != ZKError.OK:
                raise ServerInternalError(f"Unable to change pipeline to running status, error is {error}")



    def stop(self, request:HttpRequest, id:str, **kwargs):
        with zkdb(**settings.FIREBIRD_CONFIG['zookeeper']) as db:
            error, pipeline = db.get_pipeline(id)

            if error != ZKError.OK:
                raise BadRequest(f"Unable to get pipeline, error is {error}")

            if not pipeline['is_running']:
                raise BadRequest(f"Pipeline is not running!")


            for generator_id in get_generator_ids(pipeline):
                name = f"firebird-pipeline--{id}--{generator_id}"
                K8ACCESSOR.delete_statefulset(namespace=pipeline["namespace_name"], name=name)

            name = f"firebird-pipeline--{id}"
            K8ACCESSOR.delete_deployment(namespace=pipeline["namespace_name"], name=name)

            error = db.set_pipeline_is_running(id, False)
            if error != ZKError.OK:
                raise BadRequest(f"Unable to change pipeline to stopped status, error is {error}")
