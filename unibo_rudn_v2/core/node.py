from enum import Enum

from math import sqrt

from unibo_rudn_v2.core.position import Position


class Node:
    def __init__(self, id, radius, input):
        self.input = input
        self.state = NodeState.IDLE

        self.id = id
        self.position = Position(radius)
        self.event_time = 0.0
        self.attempt = 0

        self.has_collision = False
        self.has_data_to_transmit = True

        self.statistics = NodeStatistics()

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
    TX = "tx"
    OUT = "out"
    SUCCESS = "success"
    FAILURE = "failure"

class NodeStatistics:
    def __init__(self):
        self.pacchTX = 0
        self.pacchRX = 0
        self.pacchColl = 0

        # self.total_cycle_count = None
        # self.total_idle_cycle_count = None
        #
        # self.probability_of_rts_collision = 0.0
        # self.probability_of_rts_success = 0.0
        #
        # self.probability_of_failure = 0.0 # cycle failure
        # self.probability_of_success = 0.0 # cycle success
        # self.probability_of_wait = 0.0
        #
        # self.cycle_time2 = 0.0
        # self.cycle_time = 0.0
        # self.idle_time = 0.0
        # self.backoff_time = 0.0
        # self.rts_time = 0.0
        # self.cts_time = 0.0
        # self.out_time = 0.0
        # self.data_time = 0.0
        # self.ack_time = 0.0
        # self.wait_time = 0.0
        # self.not_tx_rx_time = 0.0 # part of cycle time where there are not RTS/CTS/DATA/ACK transmission
        # self.channel_busy_time = 0.0
        #
        # self.total_idle_time = 0.0
        # self.total_backoff_time = 0.0
        # self.total_rts_time = 0.0
        # self.total_cts_time = 0.0
        # self.total_out_time = 0.0
        # self.total_data_time = 0.0
        # self.total_ack_time = 0.0
        # self.total_wait_time = 0.0
        # self.total_not_tx_rx_time = 0.0
        # self.total_failure_cycle_time = 0.0
        # self.total_success_cycle_time = 0.0
        #
        # self.data_transmissions_count = 0.0
        # self.parallel_transmitting_nodes = 0.0
        #
        # self.total_transmitted_rts_messages = 0
        # self.rts_collision_messages = 0
        # self.rts_success_messages = 0
        #
        # self.trajectory_times = {}
        # self.trajectory_cycle_count = {}
        #
        # self.pacchRx = 0
        # self.pacchTx = 0
        # self.pacchColl = 0
        #
        # self.pS = 0.0
        # self.pC = 0.0

