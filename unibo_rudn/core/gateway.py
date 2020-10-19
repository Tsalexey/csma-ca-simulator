from enum import Enum

from unibo_rudn.core.position import Position


class Gateway:
    def __init__(self, input):
        self.input = input
        self.state = GatewayState.RX_RTS

        self.position = Position(0.0)
        self.event_time = None
        self.statistics = GatewayStatistics()

        self.received_rts_messages = {}

        if self.input.is_debug:
            print("# Generate gateway{x =", self.position.x, ", y = ", self.position.y, ", z = ", self.position.z, "}")


class GatewayState(Enum):
    RX_RTS = "rx rts"
    RX_DATA = "rx data"

class GatewayStatistics:
    def __init__(self):
        self.received_rts = 0.0
        self.blocked_rts = 0.0
        self.not_blocked_rts = 0.0
        self.ignored_rts = 0.0

        self.collision_time = 0.0
        self.probability_of_collision = None
        self.probability_of_collision_by_time = None
