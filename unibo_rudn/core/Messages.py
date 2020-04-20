from enum import Enum


class MessageType(Enum):
    beacon = "Beacon"
    rts = "RTS"
    cts = "CTS"


class BeaconMessage:
    def __init__(self, id, generated_at):
        self.id = id
        self.type = MessageType.beacon
        self.generated_at = generated_at
        self.node_arrival_time = None


class RTSMessage:
    def __init__(self, id, generated_at):
        self.id = id
        self.type = MessageType.rts
        self.generated_at = generated_at
        self.sent_from_node_at = None
        self.arrived_to_gateway_at = None
        self.processed_at_gateway_at = None
        self.propagation_time = None
        self.transmision_time = None

class CTSMessage:
    def __init__(self, id, generated_at, channel_busy_time):
        self.id = id
        self.type = MessageType.cts
        self.generated_at = generated_at
        self.sent_from_gateway_at = generated_at
        self.arrived_to_node_at = None
        self.channel_busy_time = channel_busy_time
        self.propagation_time = None
        self.transmision_time = None