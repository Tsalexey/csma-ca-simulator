from enum import Enum

from math import sqrt

from cyclic.core.position import Position


class Node:
    def __init__(self, id, radius, input):
        self.input = input
        self.state = NodeState.IDLE

        self.id = id
        self.position = Position(radius)
        self.event_time = 0.0
        self.cycle = 0
        self.idle_cycle = 0
        self.attempt = 0
        self.statistics = NodeStatistics()

        self.statistics.trajectory_times["idle"] = 0.0
        for i in range(1, input.N_retry+2):
            self.statistics.trajectory_times["success with " + str(i) + " rts"] = 0.0
        self.statistics.trajectory_times["failure"] = 0.0

        self.statistics.trajectory_cycle_count["idle"] = 0
        for i in range(1, input.N_retry+2):
            self.statistics.trajectory_cycle_count["success with " + str(i) + " rts"] = 0
        self.statistics.trajectory_cycle_count["failure"] = 0

        self.cts = None

        self.cycle_times = []
        self.cycle_start_time = None
        self.cycle_end_time = None

        if (self.input.is_debug):
            print("# Generate node{id=", self.id, ", x =", self.position.x, ", y = ", self.position.y, ", z = ", self.position.z, "}, distance = ", self.get_distance_to_gateway())

    def get_distance_to_gateway(self):
        return sqrt(pow(self.position.x, 2) + pow(self.position.y, 2) + pow(self.position.z, 2))

    def get_propagation_time(self):
        """
        Propagation time = distance / speed of light
        """
        return 0.0 # self.get_distance_to_gateway() / (3 * pow(10,8))

class NodeState(Enum):
    IDLE = "idle"
    BO = "backoff"
    TX_RTS = "tx rts"
    OUT = "out"
    RX_CTS = "rx cts"
    WAIT = "wait"
    TX_DATA = "tx data"
    SUCCESS = "success"
    FAILURE = "failure"

class NodeStatistics:
    def __init__(self):
        self.total_cycle_count = None
        self.total_idle_cycle_count = None

        self.failure_count = 0.0
        self.success_count = 0.0

        self.cycle_time2 = 0.0
        self.cycle_time = 0.0
        self.rts_time = 0.0
        self.data_time = 0.0

        self.data_transmissions_count = 0.0
        self.parallel_transmitting_nodes = 0.0

        self.trajectory_times = {}
        self.trajectory_cycle_count = {}
