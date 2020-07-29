from enum import Enum


class MessageType(Enum):
    RTS = "rts"
    CTS = "cts"
    DATA = "data"
    ACK = "ack"

class RTSMessage:
    def __init__(self, node_id):
        self.id = None
        self.node_id = node_id
        self.type = MessageType.RTS
        self.reached_gateway_at = None
        self.transmission_time = None
        self.propagation_time = None

class CTSMessage:
    def __init__(self, node_id):
        self.id = None
        self.node_id = node_id
        self.type = MessageType.CTS
        self.reached_node_at = None
        self.transmission_time = None
        self.propagation_time = None

class DataMessage:
    def __init__(self, node_id):
        self.node_id = node_id
        self.type = MessageType.DATA

class ACKMessage:
    def __init__(self, node_id):
        self.node_id = node_id
        self.type = MessageType.ACK