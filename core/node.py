from math import sqrt

import numpy

from core.position import Position


class Node:
    def __init__(self, id, radius, is_debug):
        self.is_debug = is_debug
        self.id = id
        self.position = Position(radius)
        self.T_max = 5
        if (is_debug):
            print("Node{id=", self.id, ", x =", self.position.x, ", y = ", self.position.y, ", z = ", self.position.z, "}")

    def get_propagation_time(self):
        return sqrt(pow(self.position.x, 2) + pow(self.position.y, 2) + pow(self.position.z, 2))

    def receive_beacon_message(self, current_time):
        self.beacon_receive_time = current_time + self.get_propagation_time()

    def wait_before_sending_rts(self, retry_number):
        out_time = 1
        if retry_number == 0:
            out_time = 0
        self.rts_sending_time = self.beacon_receive_time + out_time + numpy.random.uniform(0, (retry_number + 1) * self.T_max)

    def send_rts(self):
        self.rts_receiving_time = self.rts_sending_time + self.get_propagation_time()
