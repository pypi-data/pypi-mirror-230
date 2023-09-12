#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from typing import Dict, Callable
import logging
import logging.config
import importlib
from uuid import uuid4
from firebird.rabbitmq import get_connection, RabbitMQ
from firebird import zkdb, ZKError
from firebird.libs import render_template
from firebird.libs.k8 import K8ACCESSOR

logger = logging.getLogger(__name__)

def register_command(config:dict, pipeline_namespace_name:str, pipeline_image_name:str, pipeline_module_name:str):
    pipeline = importlib.import_module(pipeline_module_name).get_pipeline(None)
    pipeline_info = pipeline.to_json()

    mq = RabbitMQ(
        connection = get_connection(**config["rabbitmq"]),
        topic = pipeline.id
    )
    # create rabbitmq topic, etc
    mq.initialize()

    with zkdb(**config['zookeeper']) as db:
        error = db.register_pipeline(pipeline.id, pipeline_namespace_name, pipeline_image_name, pipeline_module_name, pipeline_info)
        if error != ZKError.OK:
            print(f"register pipeline failed, error is: {error}")

def unregister_command(config:dict, pipeline_id:str):
    with zkdb(**config['zookeeper']) as db:
        error = db.unregister_pipeline(pipeline_id)
        if error != ZKError.OK:
            print(f"unregister pipeline failed, error is: {error}")

def list_command(config):
    with zkdb(**config['zookeeper']) as db:
        pipelines = db.get_pipelines()

    for pipeline in pipelines:
        print(f"{pipeline['info']['id']}:")
        print(f"    namespace: {pipeline['namespace_name']}")
        print(f"    image    : {pipeline['image_name']}")
        print(f"    module   : {pipeline['module']}")
        print(f"    running  : {'Yes' if pipeline['is_running'] else 'No'}")
        if len(pipeline["executors"]) == 0:
            print("    executors: None")
        else:
            print("    executors:")
            for executor in pipeline["executors"]:
                executor_info = executor["info"]
                print(f"        {executor_info['id']}:")
                print(f"            start_time            = {executor_info['start_time']}")
                print(f"            pid                   = {executor_info['pid']}")
                print(f"            generator_id          = {executor_info['generator_id']}")


def get_generator_ids(pipeline):
    generator_ids = []
    for node in pipeline["info"]["nodes"]:
        input_port_count = 0
        for port in node["ports"]:
            if port["type"] == "INPUT": # hack, better use PortType enum
                input_port_count += 1
                break
        if input_port_count == 0:
            generator_ids.append(node["id"])
    return generator_ids


def stop_command(config:dict, pipeline_id:str):
    with zkdb(**config['zookeeper']) as db:
        error, pipeline = db.get_pipeline(pipeline_id)

    if error != ZKError.OK:
        print(f"Unable to get pipeline, error is {error}")
        return

    if not pipeline['is_running']:
        print(f"Pipeline is not running!")
        return

    for generator_id in get_generator_ids(pipeline):
        name = f"firebird-pipeline--{pipeline_id}--{generator_id}"
        print(f"Delete statefulset: {name}")
        K8ACCESSOR.delete_statefulset(namespace=pipeline["namespace_name"], name=name)
        print()

    name = f"firebird-pipeline--{pipeline_id}"
    print(f"Delete statefulset: {name}")
    K8ACCESSOR.delete_deployment(namespace=pipeline["namespace_name"], name=name)

    with zkdb(**config['zookeeper']) as db:
        error = db.set_pipeline_is_running(pipeline_id, False)
        if error != ZKError.OK:
            print(f"Unable to change pipeline to stopped status, error is {error}")
    print()


def start_command(config, pipeline_id, replicas):
    with zkdb(**config['zookeeper']) as db:
        error, pipeline = db.get_pipeline(pipeline_id)
    
    if error != ZKError.OK:
        print(f"Unable to get pipeline, error is {error}")
        return

    if pipeline['is_running']:
        print(f"Pipeline is already running!")
        return

    rollback_is_running = False
    try:
        with zkdb(**config['zookeeper']) as db:
            error = db.set_pipeline_is_running(pipeline_id, True)
            if error != ZKError.OK:
                print(f"Unable to change pipeline to running status, error is {error}")
                return
        rollback_is_running = True
        K8ACCESSOR.apply(
            template_name="pipeline.yaml",
            context={
                "pipeline_namespace_name": pipeline["namespace_name"],
                "pipeline_image_name": pipeline["image_name"],
                "pipeline_id": pipeline_id,
                "replicas": replicas,
                "generator_ids": get_generator_ids(pipeline)
            }
        )
        rollback_is_running = False
    finally:
        if rollback_is_running:
            with zkdb(**config['zookeeper']) as db:
                error = db.set_pipeline_is_running(pipeline_id, False)
                if error != ZKError.OK:
                    print(f"Unable to rollback pipeline's is_running status, error is {error}")

