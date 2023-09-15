#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from typing import Dict, Optional
import logging

###################################################################
# the main process need to monitor child process
# - if main process got SIGTERM (killed), it will set quit_requested to True
#   this variable has been shared with child processes, so child process can check it and quit
#   accordingly
# - if a child process is terminated. The main process knows it
#   TODO: the main process can check the child process exit code and retry it if needed
# - if a child process got SIGTERM, it will quit.
###################################################################
logger = logging.getLogger(__name__)

import importlib
import signal
from multiprocessing import Value
from uuid import uuid4
from firebird import zkdb, Node

from firebird.rabbitmq import get_connection, RabbitMQ

__EXECUTOR_CONTEXT = {
    'quit_requested': Value('b', False)
}
    
def __request_executor_shutdown(signal_umber, frame):
    _, _ = signal_umber, frame
    __EXECUTOR_CONTEXT['quit_requested'].value = True
    logger.info("executor: Got SIGTERM")


def executor_main(config:dict, pipeline_module_name:str, pipeline_id:str, node: Optional[Node]):
    signal.signal(signal.SIGTERM, __request_executor_shutdown)  # regular kill command
    quit_requested = __EXECUTOR_CONTEXT['quit_requested']

    mq = RabbitMQ(
        connection = get_connection(**config["rabbitmq"]),
        topic = pipeline_id
    )
    # Each pipeline module has a method get_pipeline() wich returns a Pipeline instance
    pipeline = importlib.import_module(pipeline_module_name).get_pipeline(mq)
    
    if node is None:
        # for puller
        pipeline.message_loop(quit_requested)
    else:
        # for generator
        generator = pipeline[node.id]
        generator.pump(quit_requested)

# This is the main entry for pipeline pod
def execute_pipeline(
    config:dict, 
    *, 
    pipeline_id:str, 
    generator_id:Optional[str]
):
    logger.info(f"execute_pipeline: enter")
    logger.info(f"execute_pipeline: pipeline_id={pipeline_id}, generator_id={generator_id}")
    zk_config = config['zookeeper']

    with zkdb(**zk_config) as db:
        pipeline_registry = db.get_pipeline(pipeline_id)

        pipeline_module_name = pipeline_registry.module
        logger.info(f"execute_pipeline: pipeline_module_name={pipeline_module_name}")

        # try to import the pipeline
        pipeline = importlib.import_module(pipeline_module_name).get_pipeline(None)
        logger.info(f"execute_pipeline: pipeline acquired")

        executor_id = str(uuid4())
        logger.info(f"execute_pipeline: executor_id={executor_id}")
        db.register_executor(pipeline_id, executor_id, generator_id)
        logger.info(f"execute_pipeline: executor {executor_id} registered")

    try:
        # if this is for puller, then generator_id is None
        node = None if generator_id is None else pipeline[generator_id]
        executor_main(config, pipeline_module_name, pipeline_id, node)
    finally:
        with zkdb(**zk_config) as db:
            db.unregister_executor(pipeline_id, executor_id)
            logger.info(f"execute_pipeline: executor {executor_id} unregistered")
            logger.info(f"execute_pipeline: exit")

