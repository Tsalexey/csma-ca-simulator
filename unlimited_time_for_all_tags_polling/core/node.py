from math import sqrt

import numpy

from unlimited_time_for_all_tags_polling.core.Messages import RTSMessage
from unlimited_time_for_all_tags_polling.core.position import Position


class Node:
    def __init__(self, id, radius, is_debug):
        self.is_debug = is_debug
        self.id = id
        self.position = Position(radius)
        self.T_max = 15
        self.rts_generation_intensity = 5
        self.retry_number = 0
        self.t_out = 10
        self.next_rts_generation_time = None
        self.is_user_data_sent = False

        # statistic collection part
        self.sent_rts_messages = []
        self.received_cts_messages = []
        self.beacon_message = None
        self.last_generated_rts_message = None
        self.cts_message = None

        if (self.is_debug):
            print("Node{id=", self.id, ", x =", self.position.x, ", y = ", self.position.y, ", z = ", self.position.z, "}")

    def push_beacon_message(self, beacon_message):
        beacon_message.arrived_to_node_at = beacon_message.generated_at + self.get_propagation_time()
        self.beacon_message = beacon_message
        self.next_rts_generation_time = self.beacon_message.arrived_to_node_at

    def push_cts_message(self, cts_message):
        cts_message.arrived_to_node_at = cts_message.sent_from_gateway_at + self.get_propagation_time()
        self.cts_message = cts_message

    def generate_rts_message(self):
        generated_at = self.next_rts_generation_time + self.get_tau_g_RTS(self.rts_generation_intensity)
        sent_from_node_at = generated_at + self.get_tau_w(self.retry_number, self.T_max)
        arrived_to_gateway_at = sent_from_node_at + self.get_propagation_time()

        rts_message = RTSMessage(self.id, generated_at)
        rts_message.sent_from_node_at = sent_from_node_at
        rts_message.arrived_to_gateway_at = arrived_to_gateway_at

        self.last_generated_rts_message = rts_message
        self.next_rts_generation_time = sent_from_node_at + self.t_out
        self.retry_number = self.retry_number + 1

    def get_tau_g_RTS(self, rts_generation_intensity):
        return numpy.random.exponential(scale=1 / rts_generation_intensity)

    def get_tau_w(self, retry_number, T_max):
        return numpy.random.uniform(0, (retry_number + 1) * T_max)

    def get_propagation_time(self):
        return sqrt(pow(self.position.x, 2) + pow(self.position.y, 2) + pow(self.position.z, 2))