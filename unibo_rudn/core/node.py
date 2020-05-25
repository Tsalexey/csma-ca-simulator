from math import sqrt

import numpy

from unibo_rudn.core.Messages import RTSMessage
from unibo_rudn.core.position import Position


class Node:
    def __init__(self, id, radius, T_max, tau_g_rts, tau_out, is_debug):
        self.is_debug = is_debug
        self.id = id
        self.position = Position(radius)

        self.T_max = T_max
        self.tau_g_rts = tau_g_rts
        self.transmission_attempt = 1
        self.tau_out = tau_out

        self.next_rts_generation_time = None

        self.beacon_message = None
        self.cts_message = None
        self.ack_message = None

        # statistics
        self.ready_to_transmit_rts = {}
        self.transmitted_rts_messages = {}
        self.received_cts_messages = {}
        self.T_rts = 0.0
        self.E_tc = 0.0

        self.waiting_for_other_data_transmission_finished = None
        self.is_active = True

        self.stat_collision = []
        self.stat_success = []

        self.finished_at = None

        if (self.is_debug):
            print("# Generate node{id=", self.id, ", x =", self.position.x, ", y = ", self.position.y, ", z = ", self.position.z, "}, distance = ", self.get_distance_to_gateway())

    def get_tau_w(self, transmission_attempt, T_max):
        return get_tau_w(transmission_attempt, T_max)

    def get_propagation_time(self):
        """
        Propagation time = distance / speed og light
        """
        return self.get_distance_to_gateway() / (3 * pow(10,8))

    def get_distance_to_gateway(self):
        return sqrt(pow(self.position.x, 2) + pow(self.position.y, 2) + pow(self.position.z, 2))

def get_tau_w(transmission_attempt, T_max):
    return numpy.random.uniform(0, (transmission_attempt) * T_max)
