import csv
import random

from unibo_rudn_v2.core.node import Node, NodeState

class Statictics:
    def __init__(self):
        self.NN = 0
        self.p_mac = 0.0
        self.p_col = 0.0

class Simulation:
    def __init__(self, input):
        self.input = input
        self.statistics = Statictics()

    def run(self):
        self.statistics = Statictics()

        print("# Simulation started for ", self.input.NN, " nodes")

        for repeat in range(self.input.repeats):
            if self.input.debug_repeats:
                print("Repeat #", repeat)

            self.time = 0

            self.nodes = []
            for i in range(1, self.input.NN + 1):
                self.nodes.append(Node(i, self.input.sphere_radius, self.input))

            while self.time <= self.input.simulation_time:
                if self.input.debug_time:
                    print("Time =", self.time)

                for node in self.nodes:
                    if node.event_time == self.time:
                        if node.state == NodeState.IDLE:
                            ''' IDLE '''
                            if node.has_data_to_transmit and (random.random() < node.input.p_a):
                                node.attempt += 1

                                delay = random.randint(0, self.input.Tmax - 1)

                                if delay == 0:
                                    node.state = NodeState.TX
                                    node.has_collision = False
                                    node.has_data_to_transmit = False
                                    node.event_time = self.time + self.input.Trts

                                    node.statistics.pacchTX += 1
                                else:
                                    node.state = NodeState.BO
                                    node.event_time = self.time + delay * self.input.Tbo
                            else:
                                node.state = NodeState.IDLE
                                node.event_time = self.time + self.input.slot_time
                        if node.state == NodeState.TX:
                            ''' TX '''
                            if not node.has_collision:
                                node.state = NodeState.IDLE
                                node.event_time = self.time + self.input.Tcts + self.input.Tidle

                                node.attempt = 0
                                node.has_data_to_transmit = True

                                node.statistics.pacchRX += 1
                            else:
                                node.state = NodeState.OUT
                                node.event_time = self.time + self.input.Tout
                        if node.state == NodeState.BO:
                            ''' BO '''
                            node.state = NodeState.TX
                            node.has_collision = False
                            node.has_data_to_transmit = False
                            node.event_time = self.time + self.input.Trts

                            if node.attempt == 1:
                                node.statistics.pacchTX += 1
                        if node.state == NodeState.OUT:
                            ''' OUT '''
                            node.attempt += 1
                            node.statistics.pacchColl += 1

                            if node.attempt <= self.input.Nretx + 1:
                                delay = random.randint(0, self.input.Tmax * node.attempt - 1)

                                if delay == 0:
                                    node.state = NodeState.TX
                                    node.has_collision = False
                                    node.has_data_to_transmit = False
                                    node.event_time = self.time + self.input.Trts

                                    node.statistics.pacchTX += 1
                                else:
                                    node.state = NodeState.BO
                                    node.event_time = self.time + delay * self.input.Tbo
                            else:
                                node.state = NodeState.IDLE
                                node.event_time = self.time + self.input.slot_time

                                node.has_data_to_transmit = True
                                node.attempt = 0
                    self.check_for_collisions(node)

                self.time += self.input.slot_time

            self.calculate_statistics()
        self.normilize_statistics()

        print("# Simulation finished")

    def check_for_collisions(self, node):
        for another_node in self.nodes:
            if node.id != another_node.id and node.state == NodeState.TX and another_node.state == NodeState.TX:
                node.has_collision = True
                break

    def print(self):
        attrs = vars(self.statistics)

        for item in attrs.items():
            print("%s: %s" % item)

    def calculate_statistics(self):
        p_mac = 0.0
        p_col = 0.0

        for node in self.nodes:
            if node.statistics.pacchTX != 0:
                p_mac += node.statistics.pacchRX / node.statistics.pacchTX
            else:
                p_mac += 0

            if node.statistics.pacchRX + node.statistics.pacchColl != 0:
                p_col += node.statistics.pacchColl / (node.statistics.pacchRX + node.statistics.pacchColl)
            else:
                p_col += 0

        self.statistics.NN = self.input.NN
        self.statistics.p_mac += p_mac / len(self.nodes)
        self.statistics.p_col += p_col / len(self.nodes)

    def normilize_statistics(self):
        self.statistics.p_mac /= self.input.repeats
        self.statistics.p_col /= self.input.repeats

    def run_for_all_nodes(self, file_name):
        filename = "../results/" \
                   + file_name \
                   + "_pa[" + str(self.input.p_a) + "]" \
                   + "_sensing[" + str(self.input.sensing) + "]" \
                   + "_nodes[" + str(1) + "-" + str(self.input.NN) + "]" \
                   + "_retry[" + str(self.input.Nretx) + "]" \
                   + "_repeats[" + str(self.input.repeats) + "]" \
                   + "_time[" + str(self.input.simulation_time) + "].csv"

        kwargs = {'newline': ''}
        mode = 'w'
        with open(filename, mode, **kwargs) as fp:
            writer = csv.writer(fp, delimiter=';')

            writer.writerow(list(vars(self.statistics).keys())) # output first line with description

            max_nodes = self.input.NN
            for n in range(1, max_nodes + 1):
                self.input.NN = n
                self.run()
                writer.writerow(list(vars(self.statistics).values()))


