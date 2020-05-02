from enum import Enum
import uuid

class MessageType(Enum):
    beacon = "Beacon"
    rts = "RTS"
    cts = "CTS"
    ack = "ACK"


class BeaconMessage:
    def __init__(self, id, generated_at, transmission_time):
        self.id = id
        self.type = MessageType.beacon
        self.generated_at = generated_at
        self.transmission_time = transmission_time
        self.node_arrival_time = None

class RTSMessage:
    def __init__(self, id, generated_at):
        self.rts_id = "#" + str(id) + "_" + str(generated_at)
        self.id = id
        self.attempt_number = None
        self.type = MessageType.rts
        self.generated_at = generated_at
        self.sent_from_node_at = None
        self.arrived_to_gateway_at = None
        self.processed_at_gateway_at = None
        self.propagation_time = None
        self.transmission_time = None

class CTSMessage:
    def __init__(self, id, generated_at, transmission_time):
        self.id = id
        self.type = MessageType.cts
        self.rts_attempt_number = None
        self.generated_at = generated_at
        self.propagation_time = None
        self.transmission_time = transmission_time
        self.arrived_at = None

class ACKMessage:
    def __init__(self, id, generated_at, transmission_time, propagation_time):
        self.id = id
        self.type = MessageType.ack
        self.generated_at = generated_at
        self.propagation_time = propagation_time
        self.transmission_time = transmission_time
        self.arrived_at = self.generated_at + self.propagation_time + self.transmission_time