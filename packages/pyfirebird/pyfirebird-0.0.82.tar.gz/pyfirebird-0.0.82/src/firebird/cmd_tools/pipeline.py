#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging
import logging.config
import argparse
import importlib
import os
import sys
import json

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

    impl = importlib.import_module("firebird.cmd_tools.pipeline_impl")

    if action == "register":
        check_args(args, ["pipeline_namespace_name", "pipeline_image_name", "pipeline_module_name"])
        impl.register_command(
            config, 
            args.pipeline_namespace_name, 
            args.pipeline_image_name, 
            args.pipeline_module_name
        )
    if action == "unregister":
        check_args(args, ["pipeline_id"])
        impl.unregister_command(config, args.pipeline_id)
    elif action == "list":
        impl.list_command(config)
    elif action == "start":
        check_args(args, ["pipeline_id"])
        impl.start_command(config, args.pipeline_id, args.replicas)
    elif action == "stop":
        check_args(args, ["pipeline_id"])
        impl.stop_command(config, args.pipeline_id)


if __name__ == '__main__':
    main()
