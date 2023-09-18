from abc import ABC, abstractmethod
from typing import List, Any, Optional, Dict, Set, Union, Tuple
from enum import Enum
from multiprocessing.sharedctypes import Synchronized
from datetime import datetime

from firebird.rabbitmq import RabbitMQ
########################################################################
# Node:         a node of a pipeline
# Sink:         a node without output ports
# Generator:    a node without input ports
# Port:         input port can connect to output port
#
# User do not derive class from Port
########################################################################

DEFAULT_INPUT_PORT_ID   = "input"
DEFAULT_OUTPUT_PORT_ID  = "output"

class PipelineException(Exception):
    pass

class PipelineBadArgument(PipelineException):
    pass

class PortType(Enum):
    INPUT = 1
    OUTPUT = 2

class NPId: # node id and port id
    node_id:str
    port_id:str

    def __init__(self, *, node_id:str, port_id:str):
        self.node_id = node_id
        self.port_id = port_id

    def to_json(self):
        return {"node_id": self.node_id, "port_id": self.port_id}
    
    @classmethod
    def from_json(cls, payload):
        return cls(node_id=payload['node_id'], port_id=payload['port_id'])


class PortInfo:
    id:str
    type:PortType
    connected_ports:List[NPId]

    def __init__(self, *, id:str, type:PortType, connected_ports:List[NPId]):
        self.id = id
        self.type = type
        self.connected_ports = connected_ports
    
    def to_json(self):
        return {
            "id": self.id,
            "type": self.type.name,
            "connected_ports": [item.to_json() for item in self.connected_ports]
        }
    
    @classmethod
    def from_json(cls, payload):
        return cls(
            id=payload['id'],
            type=PortType[payload['type']],
            connected_ports=[NPId.from_json(item) for item in payload["connected_ports"]]
        )

class NodeInfo:
    id:str
    title:str
    description:str
    ports: List[PortInfo]

    def __init__(self, *, id:str, title:str, description:str, ports:List[PortInfo]):
        self.id = id
        self.title = title
        self.description = description
        self.ports = ports

    def is_generator(self):
        for port in self.ports:
            if port.type == PortType.INPUT:
                return False
        return True

    def to_json(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "ports": [port.to_json() for port in self.ports]
        }

    @classmethod
    def from_json(cls, payload):
        return cls(
            id=payload['id'],
            title=payload['title'],
            description=payload['description'],
            ports=[PortInfo.from_json(item) for item in payload["ports"]]
        )

class PipelineInfo:
    id:str
    title:str
    description:str
    nodes:List[NodeInfo]

    def __init__(self, *, id:str, title:str, description:str, nodes:List[NodeInfo]):
        self.id = id
        self.title = title
        self.description = description
        self.nodes = nodes
    
    def get_generators(self):
        return [node for node in self.nodes if node.is_generator()]

    def to_json(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "nodes": [node.to_json() for node in self.nodes]
        }
    
    @classmethod
    def from_json(cls, payload):
        return cls(
            id=payload['id'],
            title=payload['title'],
            description=payload['description'],
            nodes=[NodeInfo.from_json(item) for item in payload["nodes"]]
        )

class K8SState:
    deployment_name:str       # k8s deployment name, for puller
    generators:Dict[str, str] # for all generator statefulsets
                              # ket is generator_id, value is the statefulset name
    
    def __init__(self, *, deployment_name:str, generators:Dict[str, str]):
        self.deployment_name = deployment_name
        self.generators = generators
    
    def to_json(self):
        return {"deployment_name": self.deployment_name, "generators": self.generators}
    
    @classmethod
    def from_json(cls, payload):
        return cls(deployment_name=payload["deployment_name"], generators=payload["generators"])

class PipelineRegistry:
    pipeline_info:PipelineInfo
    module:str
    namespace_name:str
    image_name:str
    is_running:bool
    k8s_state:K8SState
    executors:List["Executor"]

    def __init__(
        self, 
        *, 
        pipeline_info:PipelineInfo, 
        module:str, 
        namespace_name:str, 
        image_name:str, 
        is_running:bool, 
        k8s_state:K8SState,
        executors:List["Executor"]=[]
    ):
        self.pipeline_info = pipeline_info
        self.module = module
        self.namespace_name = namespace_name
        self.image_name = image_name
        self.is_running = is_running
        self.k8s_state = k8s_state
        self.executors = executors
    
    def to_json(self):
        return {
            "pipeline_info": self.pipeline_info.to_json(),
            "module": self.module,
            "namespace_name": self.namespace_name,
            "image_name": self.image_name,
            "is_running": self.is_running,
            "k8s_state": self.k8s_state.to_json(),
            "executors": [executor.to_json() for executor in self.executors]
        }

    def from_json(cls, payload):
        return cls(
            pipeline_info=PipelineInfo.from_json(payload["pipeline_info"]),
            module=payload["module"],
            namespace_name=payload["namespace_name"],
            image_name=payload["image_name"],
            is_running=payload["image_name"],
            k8s_state=K8SState.from_json(payload["k8s_state"]),
            executors=[Executor.from_json(item) for item in payload["executors"]]
        )

class Executor:
    id:str
    start_time:datetime
    pid:int
    generator_id:Optional[str]

    def __init__(self, *, id, start_time:datetime, pid:int, generator_id:Optional[str]):
        self.id = id
        self.start_time = start_time
        self.pid = pid
        self.generator_id = generator_id
    
    def to_json(self):
        return {
            "id": self.id,
            "start_time": self.start_time.strftime("%Y-%m-%d %H:%M:%S.%f"),
            "pid": self.pid,
            "generator_id": self.generator_id
        }

    @classmethod
    def from_json(cls, payload):
        return cls(
            id=payload['id'],
            start_time=datetime.strptime(payload["start_time"], "%Y-%m-%d %H:%M:%S.%f"),
            pid=payload['pid'],
            generator_id=payload['generator_id']
        )

class Node(ABC):
    # Each input port has a unique name among input ports
    # Each output port has a unique name among output ports
    # Sink does not have output ports
    # Source does not have input ports
    pipeline:"Pipeline"               # Pipeline owns this node
    id:str
    title:str
    description:str
    _ports_dict:Dict[str, "Port"]
    input_port_ids:Tuple[str]
    output_port_ids:Tuple[str]

    def __init__(self, 
        *, 
        pipeline:"Pipeline", 
        id:str,
        title:str="",
        description:str="",
        input_port_ids:List[str]=[DEFAULT_INPUT_PORT_ID],
        output_port_ids:List[str]=[DEFAULT_OUTPUT_PORT_ID]
    ):
        # validate input port ids and output port ids
        all_port_id_set = set(input_port_ids + output_port_ids)
        if len(all_port_id_set) < len(input_port_ids) + len(output_port_ids):
            raise PipelineBadArgument("Duplicate port ids found!")

        self.pipeline = pipeline
        self.id = id
        self.title = title
        self.description = description
        self.input_port_ids    = tuple(input_port_ids)
        self.output_port_ids   = tuple(output_port_ids)
        self._ports_dict = {}

        for port_id in input_port_ids:
            self._ports_dict[port_id] = Port(node=self, id=port_id, type=PortType.INPUT)

        for port_id in output_port_ids:
            self._ports_dict[port_id] = Port(node=self, id=port_id, type=PortType.OUTPUT)
        
        pipeline._add_node(self)

    def get_info(self) -> NodeInfo:
        return NodeInfo(
            id=self.id, 
            title=self.title,
            description=self.description,
            ports=[
                port.get_info() for _, port in self._ports_dict.items()
            ]
        )
    
    def __getitem__(self, port_id:str) -> "Port":
        ret = self._get_port(port_id)
        if ret is None:
            raise PipelineBadArgument(f"Node(id={self.id} does not have port(id={port_id}))")
        return ret
   
    @property
    def input(self) -> "Port":
        # return default input port
        return self[DEFAULT_INPUT_PORT_ID]
    
    @property
    def output(self) -> "Port":
        # return default output port
        return self[DEFAULT_OUTPUT_PORT_ID]
   
    def _get_port(self, id:str) -> Optional["Port"]:
        # get input port by name
        return self._ports_dict.get(id)

    @abstractmethod
    def on_message(self, port_id:str, data:Any):
        # data arrives form input port with port_id
        pass

    def __lshift__(
        self, 
        other:Union[
            Union["Node", "Port"], 
            List[Union["Node", "Port"]]
        ]
    ):
        # for
        #     self << other_port
        #     self << other_node
        #     self << [other_port1, other_port2, other_node1, other_node2]
        if isinstance(other, list):
            for t in other:
                t._connect(self)
            return other

        other._connect(self)
        return other

    def __rshift__(
        self, 
        other:Union[
            Union["Node", "Port"], 
            List[Union["Node", "Port"]]
        ]
    ):
        # for
        #     self >> other_port
        #     self >> other_node
        #     self >> [other_port1, other_port2, other_node1, other_node2]
        if isinstance(other, list):
            for t in other:
                self._connect(t)
            return other

        self._connect(other)
        return other

    def __rlshift__(self, others:List[Union["Node", "Port"]]):
        # for
        #     [other_port1, other_port2, other_node1, other_node2] << self
        for other in others:
            self._connect(other)
        return self

    def __rrshift__(self, others:List[Union["Node", "Port"]]):
        # for
        #     [other_port1, other_port2, other_node1, other_node2] >> self
        for other in others:
            other._connect(self)
        return self

    def _connect(self, other: Union["Node", "Port"]):
        src = self.output
        src._connect(other)
    
    def emit(self, payload:Any, port_id:str=DEFAULT_OUTPUT_PORT_ID):
        # payload is a json object
        port = self[port_id]
        port.emit(payload)
       
    def is_generator(self):
        return isinstance(self, Generator)

class Sink(Node):
    def __init__(self, 
        *,
        pipeline:"Pipeline",
        id:str,
        title:str="",
        description:str="",
        input_port_ids:List[str]=[DEFAULT_INPUT_PORT_ID]
    ):
        super().__init__(
            pipeline=pipeline,
            id=id,
            title=title,
            description=description,
            input_port_ids=input_port_ids, 
            output_port_ids=[],
        )

class Generator(Node):
    def __init__(self, 
        *,
        pipeline:"Pipeline",
        id:str,
        title:str="",
        description:str="",
        output_port_ids:List[str]=[DEFAULT_OUTPUT_PORT_ID]
    ):
        super().__init__(
            pipeline=pipeline,
            id=id,
            title=title,
            description=description,
            input_port_ids=[], 
            output_port_ids=output_port_ids
        )

    def on_message(self, port_id:str, data:Any):
        raise PipelineBadArgument("Generator cannot process data")

    @abstractmethod
    def pump(self, quit_requested: Synchronized):
        """
        Let the source to collect data and emit data

        quit_requested: a boolean shared value
        """
        pass


class Port:
    node:"Node"   # Node owns this port
    id:str
    type:PortType
    _connected_ports: Set["Port"]

    def __init__(self, *, node:"Node", id:str, type:PortType):
        self.node       = node
        self.id         = id
        self.type       = type
        self._connected_ports:Set["Port"] = set()

    def get_info(self):
        return PortInfo(
            id=self.id,
            type=self.type,
            connected_ports=[NPId(node_id=p.node.id, port_id=p.id) for p in self._connected_ports]
        )

    def __lshift__(
        self, 
        other:Union[
            Union["Node", "Port"], 
            List[Union["Node", "Port"]]
        ]
    ):
        # for 
        #    self << other_port
        #    self << other_node
        #    self << [other_port1, other_port2, other_node1, other_node2]
        if isinstance(other, list):
            for t in other:
                t._connect(self)
            return other
        
        other._connect(self)
        return other
        
    def __rshift__(
        self, 
        other:Union[
            Union["Node", "Port"], 
            List[Union["Node", "Port"]]
        ]
    ):
        # for
        #    self >> other_port
        #    self >> other_node
        #    self >> [other_port1, other_port2, other_node1, other_node2]
        if isinstance(other, list):
            for t in other:
                self._connect(t)
            return other

        self._connect(other)
        return other

    def __rlshift__(self, others:List[Union["Node", "Port"]]):
        # for
        #     [other_port1, other_port2, other_node1, other_node2] << self
        for other in others:
            self._connect(other)
        return self

    def __rrshift__(self, others:List[Union["Node", "Port"]]):
        # for
        #     [other_port1, other_port2, other_node1, other_node2] >> self
        for other in others:
            other._connect(self)
        return self

    def _connect(self, other: Union["Node", "Port"]):
            
        if isinstance(other, Port):
            dst = other
        elif isinstance(other, Node):
            dst = other.input
        else:
            raise PipelineBadArgument(f"Can only connect to Port or Node, but got {type(other).__name__}")
        
        if self.type != PortType.OUTPUT:
            raise PipelineBadArgument("Source port MUST be output port!")
        if dst.type != PortType.INPUT:
            raise PipelineBadArgument("Destination port MUST be input port!")

        dst._connected_ports.add(self)
        self._connected_ports.add(dst)

    
    def emit(self, payload:Any):
        # payload is a JSON object
        if self.type != PortType.OUTPUT:
            raise PipelineBadArgument("Can only emit data to output port!")

        pipeline = self.node.pipeline

        for port in self._connected_ports:
            pipeline.mq.produce({
                "from": {
                    "node": self.node.id,
                    "port": self.id
                },
                "to": {
                    "node": port.node.id,
                    "port": port.id
                },
                "payload": payload
            })
    
    
class Pipeline:
    id:str
    title:str
    description:str
    mq:Optional[RabbitMQ]
    _node_dict: Dict[str, Node]

    def __init__(self, *, id:str, mq:Optional[RabbitMQ]=None, title:str="", description:str=""):
        self.id = id
        self.title = title
        self.description = description
        self.mq:RabbitMQ  = mq
        self._node_dict:Dict[str, Node] = {}
    
    def get_info(self):
        return PipelineInfo(
            id=self.id,
            title=self.title,
            description=self.description,
            nodes=[node.get_info() for _, node in self._node_dict.items()]
        )

    def message_loop(self, quit_requested: Synchronized):
        self.mq.consume(self.on_message, quit_requested)
    
    def on_message(self, envelope):
        node = self._node_dict[envelope['to']['node']]
        node.on_message(
            envelope["to"]["port"],
            envelope["payload"]
        )

    def _add_node(self, node:Node):
        # add a node to the pipeline
        if node.id in self._node_dict:
            raise PipelineBadArgument(f"Node {node.id} already exist!")
        self._node_dict[node.id] = node
    
    
    def __getitem__(self, node_id:str) -> Optional[Node]:
        ret = self._node_dict.get(node_id)
        if ret is None:
            raise PipelineBadArgument(f"Pipeline(id={self.id} does not have node(id={node_id}))")
        return ret
