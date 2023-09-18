import logging
import json
import graphviz
import os
import tempfile
import xml.dom.minidom

from .api_base import RESTAPIBase

from django.http  import HttpRequest
from django.core.exceptions import BadRequest
from firebird.core_apis import CoreAPIs, CoreAPIInvalidArguments
from firebird.base import PortType

logger = logging.getLogger(__name__)

class PipelinesAPI(RESTAPIBase):
    core_api: CoreAPIs

    def __init__(self, core_api:CoreAPIs):
        self.core_api = core_api

    def list(self, request:HttpRequest, **kwargs):
        return {
            "pipelines": [
                pipeline.to_json() for pipeline in self.core_api.list_pipelines()
            ]
        }

    def get(self, request:HttpRequest, id:str, **kwargs):
        try:
            pipeline_registry = self.core_api.get_pipeline(id)

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
                    for node in pipeline_registry.pipeline_info.nodes:
                        g.node(node.id, f"{node.id}\n{node.title}", shape="box", href="#", style="filled", fillcolor="green")

                        for port in node.ports:
                            if port.type == PortType.OUTPUT:
                                for connected_port in port.connected_ports:
                                    edges.add((node.id, connected_port.node_id))
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
                "pipeline": pipeline_registry.to_json(),
                "svg_lr": svgs[0],
                "svg_tb": svgs[1],
            }
        except CoreAPIInvalidArguments as e:
            raise BadRequest(e.args[0]) from e

    def start(self, request:HttpRequest, id:str, **kwargs):
        try:
            return self.core_api.start_pipeline(id)
        except CoreAPIInvalidArguments as e:
            raise BadRequest(e.args[0]) from e

    def stop(self, request:HttpRequest, id:str, **kwargs):
        try:
            return self.core_api.stop_pipeline(id)
        except CoreAPIInvalidArguments as e:
            raise BadRequest(e.args[0]) from e
