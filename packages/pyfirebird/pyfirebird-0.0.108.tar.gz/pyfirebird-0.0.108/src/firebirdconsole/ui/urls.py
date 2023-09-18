from django.urls import path
from . import views
from .views import apis
from firebird.core_apis import CoreAPIs
from firebird.libs.k8 import K8Accessor
from django.conf import settings

pipelines = apis.PipelinesAPI(
    CoreAPIs(
        zk_config=settings.FIREBIRD_CONFIG['zookeeper'],
        k8_accessor=K8Accessor()
    )
)

urlpatterns = [
    path('', views.home, name='home'),
    path('pipelines/<str:pipeline_id>', views.pipeline, name='pipeline'),

    path('apis/pipelines', pipelines, name='api.pipelines'),
    path('apis/pipelines/<str:id>', pipelines, name='api.pipeline'),
]
