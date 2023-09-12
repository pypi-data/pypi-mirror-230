from django.urls import path
from . import views
from .views import apis

pipelines = apis.PipelinesAPI()

urlpatterns = [
    path('', views.home, name='home'),
    path('pipelines/<str:pipeline_id>', views.pipeline, name='pipeline'),

    path('apis/pipelines', pipelines, name='api.pipelines'),
    path('apis/pipelines/<str:id>', pipelines, name='api.pipeline'),
]
