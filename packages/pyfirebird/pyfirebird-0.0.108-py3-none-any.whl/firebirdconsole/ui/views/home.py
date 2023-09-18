from django.http  import HttpRequest, HttpResponse
from firebirdconsole.ui.view_tools import render_application
from django.conf import settings

def home(request:HttpRequest)->HttpResponse:
    return render_application(
        request, 
        scripts = [f'{settings.CONSOLE_URI_BASE}/static/js-bundle/home.js'], 
        sub_title='home'
    )
