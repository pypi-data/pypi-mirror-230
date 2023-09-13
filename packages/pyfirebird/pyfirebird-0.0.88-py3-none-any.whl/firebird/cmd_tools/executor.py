#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging
import logging.config
import argparse
import importlib

import json
import os
import sys

def main():
    parser = argparse.ArgumentParser(
        description='Pipeline executor'
    )
    parser.add_argument(
        "-cd", "--config-dir", type=str, default=os.path.expanduser("~/.firebird"), required=False,
        help="Configuration directory"
    )
    parser.add_argument(
        "-pid", "--pipeline-id", type=str, required=True, help="Pipeline ID"
    )
    parser.add_argument(
        "-gid", "--generator-id", type=str, help="Generator ID"
    )
    args = parser.parse_args()

    # config log
    log_config_filename = os.path.join(args.config_dir, "log_config.json")
    if os.path.isfile(log_config_filename):
        with open(log_config_filename, "rt") as f:
            LOG_CONFIG = json.load(f)
    else:
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
            "loggers": {
                "pika": {
                    "handlers": ["console"],
                    "level":    "WARNING",
                    "propagate": False
                },
                "kazoo": {
                    "handlers": ["console"],
                    "level":    "WARNING",
                    "propagate": False
                }
            }
        }
    logging.config.dictConfig(LOG_CONFIG)

    config_filename = os.path.join(args.config_dir, "config.json")
    if not os.path.isfile(config_filename):
        print(f"Unable to find config file from {config_filename}")
        sys.exit(1)

    with open(config_filename, "rt") as f:
        config = json.load(f)
    
    impl = importlib.import_module("firebird.cmd_tools.executor_impl")
    impl.execute_pipeline(
        config, 
        pipeline_id=args.pipeline_id, 
        generator_id=args.generator_id
    )


if __name__ == '__main__':
    main()
