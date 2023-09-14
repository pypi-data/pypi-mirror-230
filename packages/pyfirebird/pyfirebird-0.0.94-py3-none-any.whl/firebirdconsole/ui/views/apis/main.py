import logging
import json

from .api_base import RESTAPIBase

from django.http  import HttpRequest
from django.core.exceptions import BadRequest
from firebird.core_apis import CoreAPIs, CoreAPIInvalidArguments

logger = logging.getLogger(__name__)

class PipelinesAPI(RESTAPIBase):
    core_api: CoreAPIs

    def __init__(self, core_api:CoreAPIs):
        self.core_api = core_api

    def list(self, request:HttpRequest, **kwargs):
        return self.core_api.list_pipelines()

    def get(self, request:HttpRequest, id:str, **kwargs):
        try:
            return self.core_api.get_pipeline(id)
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
