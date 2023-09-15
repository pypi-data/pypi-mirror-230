#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging
import logging.config
import argparse
import os
import sys
import json

from firebird.core_apis import CoreAPIs
from firebird.libs.k8 import K8Accessor

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "stream"  : "ext://sys.stdout"
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
}

# logger = logging.getLogger(__name__)

def check_args(args, names):
    for name in names:
        if getattr(args, name) is None:
            print(f"Missing option --{name.repalce('_', '-')}")
            sys.exit(2)

def main():
    parser = argparse.ArgumentParser(
        description='Pipeline Tool'
    )
    parser.add_argument(
        "action", type=str, help="Specify action",
        choices=['register', 'unregister', 'list', 'start', 'stop'],
        nargs=1
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Specify if you want to show debug logs",
    )
    parser.add_argument(
        "-cd", "--config-dir", type=str, required=False,
        help="Configuration directory"
    )
    parser.add_argument(
        "-pmn", "--pipeline-module-name", type=str, required=False,
        help="Pipeline module name"
    )
    parser.add_argument(
        "-pid", "--pipeline-id", type=str, required=False, help="pipeline ID"
    )
    parser.add_argument(
        "-r", "--replicas", type=int, default=1, required=False,
        help="replicas"
    )
    parser.add_argument(
        "-pnn", "--pipeline-namespace-name", type=str, required=False, help="pipeline namespace name"
    )
    parser.add_argument(
        "-pin", "--pipeline-image-name", type=str, required=False, help="pipeline image name"
    )
    parser.add_argument(
        "-eid", "--executor-id", type=str, required=False, help="Executor ID"
    )
    args = parser.parse_args()
    action = args.action[0]

    if args.debug:
        logging.config.dictConfig(LOG_CONFIG)
    
    config_dir = args.config_dir if args.config_dir else os.path.expanduser("~/.firebird")
    config_filename = os.path.join(config_dir, "config.json")
    if not os.path.isfile(config_filename):
        print(f"Unable to find config file from {config_filename}")
        sys.exit(1)

    with open(config_filename, "rt") as f:
        config = json.load(f)
    
    if action == "register":
        # register command runs in pipeline image and they do not have access to kubernete cluster
        core_apis = CoreAPIs(
            zk_config=config['zookeeper'],
            k8_accessor=None,
            rabbitmq_config=config['rabbitmq']
        )
    else:
        core_apis = CoreAPIs(
            zk_config=config['zookeeper'],
            k8_accessor=K8Accessor(),
            rabbitmq_config=config['rabbitmq']
        )

    if action == "register":
        check_args(args, ["pipeline_namespace_name", "pipeline_image_name", "pipeline_module_name"])
        core_apis.register_pipeline(
            args.pipeline_namespace_name, 
            args.pipeline_image_name, 
            args.pipeline_module_name
        )
    elif action == "unregister":
        check_args(args, ["pipeline_id"])
        core_apis.unregister_pipeline(args.pipeline_id)
    elif action == "list":
        for pipeline_registry in core_apis.list_pipelines():
            print(f"{pipeline_registry.pipeline_info.id}:")
            print(f"    namespace: {pipeline_registry.namespace_name}")
            print(f"    image    : {pipeline_registry.image_name}")
            print(f"    module   : {pipeline_registry.module}")
            print(f"    running  : {'Yes' if pipeline_registry.is_running else 'No'}")
            k8s_state = pipeline_registry.k8s_state
            print(f"    Kubernetes")
            for generator_id, statefulset_name in k8s_state.generators.items():
                print(f"        {statefulset_name}: {generator_id}")
            deployment_name = k8s_state.deployment_name
            if deployment_name:
                print(f"        {deployment_name}: puller")
            if len(pipeline_registry.executors) == 0:
                print("    executors: None")
            else:
                print("    executors:")
                for executor in pipeline_registry.executors:
                    print(f"        {executor.id}:")
                    print(f"            start_time            = {executor.start_time}")
                    print(f"            pid                   = {executor.pid}")
                    print(f"            generator_id          = {executor.generator_id}")
    elif action == "start":
        check_args(args, ["pipeline_id"])
        core_apis.start_pipeline(args.pipeline_id)
    elif action == "stop":
        check_args(args, ["pipeline_id"])
        core_apis.stop_pipeline(args.pipeline_id)


if __name__ == '__main__':
    main()
