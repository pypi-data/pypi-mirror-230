from typing import Dict, Callable, Any
import tempfile
import os
from kubernetes import client,config, utils
from firebird.libs import render_template

class K8Accessor:
    # To access kubernetes, you must have
    # 1: ~/.kube/config should be ready
    # 2: oci-cli must be installed and configured, so
    # 3: ~/.oci/config ~/.oci/oci_api_key.pem (referenced by ~/.oci/config) MUST be ready

    def __init__(self):
        config.load_kube_config()
        self.api = client.AppsV1Api()
        self.client = client.ApiClient()

    def delete_deployment(self, *, namespace:str, name:str) -> None:
        resp = self.api.delete_namespaced_deployment(
            name=name,
            namespace=namespace,
            pretty=True,
            body=client.V1DeleteOptions(
                propagation_policy="Foreground", grace_period_seconds=300
            ),
        )
        print(resp)
    
    def delete_statefulset(self, *, namespace:str, name:str) -> None:
        resp = self.api.delete_namespaced_stateful_set(
            name=name,
            namespace=namespace,
            pretty=True,
            body=client.V1DeleteOptions(
                propagation_policy="Foreground", grace_period_seconds=300
            ),
        )
        print(resp)


    def apply(self, *, template_name:str, context: Any) -> None:
        to_apply = render_template(template_name, context)
        with tempfile.NamedTemporaryFile(mode='wt', delete=False) as tf:
            tf.write(to_apply)
        try:
            print("Use following deployment:")
            print(os.linesep)
            print(os.linesep)
            print(to_apply)
            print(os.linesep)
            print(os.linesep)
            utils.create_from_yaml(self.client, tf.name, verbose=True)
        finally:
            os.remove(tf.name)
