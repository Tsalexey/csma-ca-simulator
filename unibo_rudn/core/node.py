from enum import Enum

from math import sqrt

from unibo_rudn.core.position import Position


class Node:
    def __init__(self, id, radius, input):
        self.input = input
        self.state = NodeState.IDLE

        self.id = id
        self.position = Position(radius)
        self.event_time = 0.0
        self.cycle_count = 0
        self.closed_idle_cycle_count = 0

        self.rts_message = None
        self.cts_message = None

        self.has_collision = False
        self.has_refrain = False

        self.attempt = 0

        self.idle_state = 0
        self.bo_state = 0
        self.rts_state = 0
        self.out_state = 0
        self.wait_state = 0
        self.refrain_state = 0
        self.cts_state = 0
        self.data_state = 0
        self.ack_state = 0
        self.success_state = 0
        self.failure_state = 0

        self.cycle_states_stacktrace = []
        self.cycle_start_time = None
        self.cycle_end_time = None

        self.statistics = NodeStatistics()
        self.idle_series_statistics = IdleSeriesStatistics()

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
    BACKOFF = "backoff"
    TX_RTS = "rts"
    OUT = "out"
    RX_CTS = "cts"
    WAIT = "wait"
    REFRAIN = "refrain"
    TX_DATA = "data"
    RX_ACK = "ack"
    SUCCESS = "success"
    FAILURE = "failure"

class NodeStatistics:
    def __init__(self):
        self.total_cycle_count = None
        self.total_idle_cycle_count = None

        self.probability_of_rts_collision = 0.0
        self.probability_of_rts_success = 0.0

        self.probability_of_failure = 0.0 # cycle failure
        self.probability_of_success = 0.0 # cycle success
        self.probability_of_wait = 0.0

        self.cycle_time2 = 0.0
        self.cycle_time = 0.0
        self.idle_time = 0.0
        self.backoff_time = 0.0
        self.rts_time = 0.0
        self.cts_time = 0.0
        self.out_time = 0.0
        self.data_time = 0.0
        self.refrain_time = 0.0
        self.ack_time = 0.0
        self.wait_time = 0.0
        self.not_tx_rx_time = 0.0 # part of cycle time where there are not RTS/CTS/DATA/ACK transmission
        self.channel_busy_time = 0.0

        self.total_idle_time = 0.0
        self.total_backoff_time = 0.0
        self.total_rts_time = 0.0
        self.total_cts_time = 0.0
        self.total_out_time = 0.0
        self.total_data_time = 0.0
        self.total_ack_time = 0.0
        self.total_wait_time = 0.0
        self.total_refrain_time = 0.0
        self.total_not_tx_rx_time = 0.0
        self.total_failure_cycle_time = 0.0
        self.total_success_cycle_time = 0.0

        self.data_transmissions_count = 0.0
        self.parallel_transmitting_nodes = 0.0

        self.total_transmitted_rts_messages = 0
        self.rts_collision_messages = 0
        self.rts_success_messages = 0

        self.trajectory_times = {}
        self.trajectory_cycle_count = {}

        self.pacchRx = 0
        self.pacchTx = 0
        self.pacchColl = 0

        self.pS = 0.0
        self.pC = 0.0

class IdleSeriesStatistics:
    def __init__(self):
        self.is_prev_cycled_closed_idle = False
        self.start_time = None
        self.end_time = None

        self.time = 0.0
        self.cycles_count = 0