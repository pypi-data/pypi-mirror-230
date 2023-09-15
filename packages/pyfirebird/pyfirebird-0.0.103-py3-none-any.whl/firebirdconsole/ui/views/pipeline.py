from django.http  import HttpRequest, HttpResponse
from firebirdconsole.ui.view_tools import render_application
from django.conf import settings

def pipeline(request:HttpRequest, pipeline_id:str)->HttpResponse:
    return render_application(
        request, 
        scripts = [f'{settings.CONSOLE_URI_BASE}/static/js-bundle/pipeline.js'], 
        sub_title='home',
        app_context = {
            "pipeline_id": pipeline_id
        }
    )
