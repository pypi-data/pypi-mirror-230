###################################################
# A Simple Rest API Framework
# Rest API Implementation must derive from RESTAPIBase
# - Rest API implementation can implement list, get, update, create, delete method
# - Rest API implementation can implement custom method as well
# - Rest API implementation http methods MUST return JSON object or throw recognized exception
# - Any unrecognized exception will be considered as server internal error and result
#   in HTTP 500 response
###################################################

import logging

from django.http import JsonResponse
from django.http  import HttpRequest, HttpResponse
from django.core.exceptions import BadRequest

logger = logging.getLogger(__name__)

class ServiceUnavailableException(Exception):
    pass

class ServerInternalError(Exception):
    pass

class RESTAPIBase:
    def list(self, request:HttpRequest, **kwargs):
        # returns JSON object
        raise BadRequest('LIST is not supported')

    def get(self, request:HttpRequest, id:str, **kwargs):
        # returns JSON object
        raise BadRequest('GET is not supported')

    def update(self, request:HttpRequest, id:str, partial:bool=False, **kwargs):
        # returns JSON object
        raise BadRequest('UPDATE is not supported')
    
    def create(self, request:HttpRequest, **kwargs):
        # returns JSON object
        raise BadRequest('CREATE is not supported')

    def delete(self, request:HttpRequest, id:str, **kwargs):
        # returns JSON object
        raise BadRequest('DELETE is not supported')

    def call_unsafe(self, request:HttpRequest, **kwargs):
        resp_json = None
        if request.method == "GET":
            id = kwargs.pop("id", None)
            if id is None:
                resp_json = self.list(request, **kwargs)
            else:
                resp_json = self.get(request, id, **kwargs)
        elif request.method == "PUT":
            id = kwargs.pop("id", None)
            assert id is not None
            resp_json = self.update(request, id, partial=False, **kwargs)
        elif request.method == "PATCH":
            id = kwargs.pop("id", None)
            assert id is not None
            resp_json = self.update(request, id, partial=True, **kwargs)
        elif request.method == "POST":
            method = request.headers.get("X-Use-Method")
            if method is None:
                resp_json = self.create(request, **kwargs)
            else:
                try:
                    m = getattr(self, method)
                except AttributeError:
                    raise BadRequest(f'{method} is not supported')
                resp_json = m(request, **kwargs)
        elif request.method == "DELETE":
            id = kwargs.pop("id", None)
            assert id is not None
            resp_json = self.delete(request, id, **kwargs)
        else:
            raise BadRequest(f'{request.method} is not recognized')
        return JsonResponse(resp_json, safe=False)

    def __call__(self, request:HttpRequest, **kwargs):
        try:
            return self.call_unsafe(request, **kwargs)
        except BadRequest as e:
            return HttpResponse(str(e), content_type="text/plain", status=400, reason=str(e))
        except ServiceUnavailableException as e:
            return HttpResponse(str(e), content_type="text/plain", status=503, reason=str(e))
        except Exception as e:
            return HttpResponse(str(e), content_type="text/plain", status=500, reason=str(e))


