import csv
import os
import random
import time
from datetime import datetime
from enum import Enum

from unibo_rudn.core.node import Node, NodeState


class Input:
    def __init__(self):
        self.simulation_time = 0.00001
        self.repeats = 10
        self.pa = 1.0
        self.start_from_NN = 1
        self.time_unit = pow(10, -9)
        self.NN = 10
        self.Nretx = 3
        self.Tslot = 3 * self.time_unit
        self.Tidle = 3 * self.time_unit
        self.Trts = 3 * self.time_unit
        self.Tcts = 3 * self.time_unit
        self.Tbo = 3 * self.time_unit
        self.Tdata = 30 * self.time_unit
        self.Tack = 3 * self.time_unit
        self.Tout = self.Tdata + self.Tack
        self.Twait = self.Tdata + self.Tack
        self.Tmax = 12

class NodeState(Enum):
    IDLE = "i"
    BACKOFF = "b"
    RTS = "r"
    OUT = "o"
    CTS = "c"
    WAIT = "w"
    DATA = "d"
    ACK = "a"

class Node:
    def __init__(self, id):
        self.id = id
        self.state = NodeState.IDLE
        self.event_time = 0
        self.attempt = 0
        self.has_collision = False
        self.channel_free = True

        self.statistics = NodeStatistics()
        self.states_history = []

class NodeStatistics:
    def __init__(self):
        self.total_rts_count = 0.0
        self.collided_rts_count = 0.0
        self.not_collided_rts_count = 0.0
        self.success_count = 0.0
        self.failure_count = 0.0

        self.free_slots_count = 0.0
        self.busy_slots_count = 0.0

        self.slots_count = 0.0
        self.idle_hits = 0.0
        self.backoff_hits = 0.0
        self.rts_hits = 0.0
        self.out_hits = 0.0
        self.cts_hits = 0.0
        self.wait_hits = 0.0
        self.data_hits = 0.0
        self.ack_hits = 0.0

        self.cycles_count = 0.0

class SimulationStatistics:
    def __init__(self):
        self.probability_of_collision = 0.0
        self.probability_of_success = 0.0
        self.probability_of_failure = 0.0
        self.probability_of_free_channel = 0.0
        self.probability_of_idle = 0.0
        self.probability_of_backoff = 0.0
        self.probability_of_rts = 0.0
        self.probability_of_out = 0.0
        self.probability_of_cts = 0.0
        self.probability_of_wait = 0.0
        self.probability_of_data = 0.0
        self.probability_of_ack = 0.0

        self.time_of_cycle = 0.0
        self.time_of_idle = 0.0
        self.time_of_backoff = 0.0
        self.time_of_rts = 0.0
        self.time_of_out = 0.0
        self.time_of_cts = 0.0
        self.time_of_wait = 0.0
        self.time_of_data = 0.0
        self.time_of_ack = 0.0

def main():
    # define folder for saving the results
    results_folder = datetime.now().strftime('%Y.%m.%d_%H-%M-%S')
    if not os.path.exists('results/' + results_folder):
        os.makedirs('results/' + results_folder)

    print("Results will be stored in results/" + results_folder)
    print("Simulation in progress")

    input = Input()

    # save input parameters to file
    for k,v in vars(input).items():
        print_to_csv_file([k, v], "input_parameters", results_folder)

    results = {}

    t1 = time.time()

    for nodes_number in range(input.start_from_NN, input.NN + 1):
        measures = []
        # create temporary input for the next scenario
        temp_input = Input()
        # update nodes number in input data
        temp_input.NN = nodes_number

        start_time = time.time()
        for i in range(1, input.repeats + 1):
            # execute single scenario
            single_measure = Simulation(temp_input, results_folder).run()
            # save statistical measures
            measures.append(single_measure)

        print("Node {0}/{1}, executed in {2}".format(nodes_number, input.NN, time.time() - start_time))

        summary = SimulationStatistics()

        # compute mean statistics
        for measure in measures:
            summary.probability_of_collision += measure.probability_of_collision
            summary.probability_of_failure += measure.probability_of_failure
            summary.probability_of_success += measure.probability_of_success
            summary.probability_of_free_channel += measure.probability_of_free_channel

            summary.probability_of_idle += measure.probability_of_idle
            summary.probability_of_backoff += measure.probability_of_backoff
            summary.probability_of_rts += measure.probability_of_rts
            summary.probability_of_out += measure.probability_of_out
            summary.probability_of_cts += measure.probability_of_cts
            summary.probability_of_wait += measure.probability_of_wait
            summary.probability_of_data += measure.probability_of_data
            summary.probability_of_ack += measure.probability_of_ack

            summary.time_of_cycle += measure.time_of_cycle
            summary.time_of_idle += measure.time_of_idle
            summary.time_of_backoff += measure.time_of_backoff
            summary.time_of_rts += measure.time_of_rts
            summary.time_of_out += measure.time_of_out
            summary.time_of_cts += measure.time_of_cts
            summary.time_of_wait += measure.time_of_wait
            summary.time_of_data += measure.time_of_data
            summary.time_of_ack += measure.time_of_ack

        summary.probability_of_collision /= len(measures)
        summary.probability_of_failure /= len(measures)
        summary.probability_of_success /= len(measures)
        summary.probability_of_free_channel /= len(measures)

        summary.probability_of_idle /= len(measures)
        summary.probability_of_backoff /= len(measures)
        summary.probability_of_rts /= len(measures)
        summary.probability_of_out /= len(measures)
        summary.probability_of_cts /= len(measures)
        summary.probability_of_wait /= len(measures)
        summary.probability_of_data /= len(measures)
        summary.probability_of_ack /= len(measures)

        summary.time_of_cycle /= len(measures)
        summary.time_of_idle /= len(measures)
        summary.time_of_backoff /= len(measures)
        summary.time_of_rts /= len(measures)
        summary.time_of_out /= len(measures)
        summary.time_of_cts /= len(measures)
        summary.time_of_wait /= len(measures)
        summary.time_of_data /= len(measures)
        summary.time_of_ack /= len(measures)

        results[nodes_number] = summary
    t2 = time.time()

    print("Total execution time: {0}".format((t2-t1)))

    # prepare first line for results description
    description = ["Node"]
    for k,v in vars(results[input.NN]).items():
        description.append(k)
    print_to_csv_file(description, "results", results_folder)

    # prepare results for the whole simulation
    for k, v in results.items():
        line = [k]
        for k2, v2 in vars(v).items():
            line.append(v2)
        print_to_csv_file(line, "results", results_folder)

class Simulation:
    def __init__(self, input, results_folder):
        self.input = input
        self.time = 0
        self.nodes = []
        self.node_state = {}
        self.history_description = ["Slot#"]
        self.results_folder = results_folder

        for i in range(1, self.input.NN + 1):
            self.history_description.append("Node#{0}".format(i))
            node = Node(i)
            node.state = NodeState.IDLE
            node.event_time = input.Tidle
            self.nodes.append(node)

        print_to_csv_file(self.history_description, "states_history_{0}_nodes".format(input.NN), results_folder)

    def run(self):
        while self.time <= self.input.simulation_time:

            states = [self.time + self.input.time_unit]

            for node in self.nodes:
                self.node_state[node.id] = node.state
                states.append(node.state.value)

            print_to_csv_file(states, "states_history_{0}_nodes".format(self.input.NN), self.results_folder)

            for node in self.nodes:
                if self.check_channel_free(node):
                    node.statistics.free_slots_count += 1
                else:
                    node.statistics.busy_slots_count += 1

                if node.event_time == self.time:
                    if self.node_state[node.id] == NodeState.IDLE:
                        self.serve_idle(node)
                    elif self.node_state[node.id] == NodeState.BACKOFF:
                        self.serve_backoff(node)
                    elif self.node_state[node.id] == NodeState.RTS:
                        self.serve_rts(node)
                    elif self.node_state[node.id] == NodeState.OUT:
                        self.serve_out(node)
                    elif self.node_state[node.id] == NodeState.CTS:
                        self.serve_cts(node)
                    elif self.node_state[node.id] == NodeState.WAIT:
                        self.serve_wait(node)
                    elif self.node_state[node.id] == NodeState.DATA:
                        self.serve_data(node)
                    elif self.node_state[node.id] == NodeState.ACK:
                        self.serve_ack(node)
                else:
                    if self.node_state[node.id] == NodeState.IDLE:
                        if node.channel_free:
                            node.channel_free = self.check_channel_free(node)

                        if not node.channel_free:
                            node.state = NodeState.IDLE
                            node.event_time = self.time + self.input.Tcts
                            node.channel_free = False
                            node.has_collision = False
                            
                    elif self.node_state[node.id] == NodeState.RTS:
                        if not node.has_collision:
                            node.has_collision = self.check_collisions(node)

                    elif self.node_state[node.id] == NodeState.BACKOFF:
                        if node.channel_free:
                            node.channel_free = self.check_channel_free(node)

                        if not node.channel_free:
                            node.state = NodeState.WAIT
                            node.event_time = self.time + self.input.Twait
                            node.channel_free = True
                            node.has_collision = False
                    elif self.node_state[node.id] == NodeState.OUT:
                        if node.channel_free:
                            node.channel_free = self.check_channel_free(node)
    
                        if not node.channel_free:
                            node.state = NodeState.OUT
                            node.event_time = self.time + self.input.Tcts
                            node.channel_free = False
                            node.has_collision = False
                    elif self.node_state[node.id] == NodeState.DATA:
                        if not node.has_collision:
                            node.has_collision = self.check_collisions(node)

            self.update_time()

        # simulation finished, calculate statistics
        simulation_statistics = SimulationStatistics()

        for node in self.nodes:
            simulation_statistics.probability_of_collision += node.statistics.collided_rts_count / node.statistics.total_rts_count
            simulation_statistics.probability_of_success += node.statistics.success_count / (
                        node.statistics.success_count + node.statistics.failure_count) if (
                        node.statistics.success_count + node.statistics.failure_count) != 0 else 1
            simulation_statistics.probability_of_failure += node.statistics.failure_count / (
                        node.statistics.success_count + node.statistics.failure_count) if (
                        node.statistics.success_count + node.statistics.failure_count) != 0 else (
                        node.statistics.success_count + node.statistics.failure_count)

            simulation_statistics.probability_of_free_channel += node.statistics.free_slots_count / (
                        node.statistics.free_slots_count + node.statistics.busy_slots_count)

            simulation_statistics.probability_of_idle += node.statistics.idle_hits * self.input.Tslot / self.time
            simulation_statistics.probability_of_backoff += node.statistics.backoff_hits * self.input.Tslot / self.time
            simulation_statistics.probability_of_rts += node.statistics.rts_hits * self.input.Tslot / self.time
            simulation_statistics.probability_of_out += node.statistics.out_hits * self.input.Tslot / self.time
            simulation_statistics.probability_of_cts += node.statistics.cts_hits * self.input.Tslot / self.time
            simulation_statistics.probability_of_wait += node.statistics.wait_hits * self.input.Tslot / self.time
            simulation_statistics.probability_of_data += node.statistics.data_hits * self.input.Tslot / self.time
            simulation_statistics.probability_of_ack += node.statistics.ack_hits * self.input.Tslot / self.time

            simulation_statistics.time_of_cycle += self.time / node.statistics.cycles_count if node.statistics.cycles_count != 0 else 1
            simulation_statistics.time_of_idle += node.statistics.idle_hits * self.input.Tslot / node.statistics.cycles_count if node.statistics.cycles_count != 0 else 1
            simulation_statistics.time_of_backoff += node.statistics.backoff_hits * self.input.Tslot / node.statistics.cycles_count if node.statistics.cycles_count != 0 else 1
            simulation_statistics.time_of_rts += node.statistics.rts_hits * self.input.Tslot / node.statistics.cycles_count if node.statistics.cycles_count != 0 else 1
            simulation_statistics.time_of_out += node.statistics.out_hits * self.input.Tslot / node.statistics.cycles_count if node.statistics.cycles_count != 0 else 1
            simulation_statistics.time_of_cts += node.statistics.cts_hits * self.input.Tslot / node.statistics.cycles_count if node.statistics.cycles_count != 0 else 1
            simulation_statistics.time_of_wait += node.statistics.wait_hits * self.input.Tslot / node.statistics.cycles_count if node.statistics.cycles_count != 0 else 1
            simulation_statistics.time_of_data += node.statistics.data_hits * self.input.Tslot / node.statistics.cycles_count if node.statistics.cycles_count != 0 else 1
            simulation_statistics.time_of_ack += node.statistics.ack_hits * self.input.Tslot / node.statistics.cycles_count if node.statistics.cycles_count != 0 else 1

        # normalize by nodes count

        simulation_statistics.probability_of_collision /= len(self.nodes)
        simulation_statistics.probability_of_success /= len(self.nodes)
        simulation_statistics.probability_of_failure /= len(self.nodes)
        simulation_statistics.probability_of_free_channel /= len(self.nodes)

        simulation_statistics.probability_of_idle /= len(self.nodes)
        simulation_statistics.probability_of_backoff /= len(self.nodes)
        simulation_statistics.probability_of_rts /= len(self.nodes)
        simulation_statistics.probability_of_out /= len(self.nodes)
        simulation_statistics.probability_of_cts /= len(self.nodes)
        simulation_statistics.probability_of_wait /= len(self.nodes)
        simulation_statistics.probability_of_data /= len(self.nodes)
        simulation_statistics.probability_of_ack /= len(self.nodes)

        simulation_statistics.time_of_cycle /= len(self.nodes)
        simulation_statistics.time_of_idle /= len(self.nodes)
        simulation_statistics.time_of_backoff /= len(self.nodes)
        simulation_statistics.time_of_rts /= len(self.nodes)
        simulation_statistics.time_of_out /= len(self.nodes)
        simulation_statistics.time_of_cts /= len(self.nodes)
        simulation_statistics.time_of_wait /= len(self.nodes)
        simulation_statistics.time_of_data /= len(self.nodes)
        simulation_statistics.time_of_ack /= len(self.nodes)

        return simulation_statistics

    def check_collisions(self, node):
        for another_node in self.nodes:
            if another_node.id != node.id and self.node_state[another_node.id] in [NodeState.RTS, NodeState.CTS, NodeState.DATA]:
                return True
        return False

    def check_channel_free(self, node):
        for another_node in self.nodes:
            if another_node.id != node.id and self.node_state[another_node.id] in [NodeState.CTS]:
                return False
        return True

    def update_time(self):
        event_time = None

        for node in self.nodes:
            if event_time is None and node.event_time is not None:
                event_time = node.event_time
            if node.event_time is not None and node.event_time < event_time:
                event_time = node.event_time

        self.time = min(self.time + self.input.Tslot, event_time)

    def serve_idle(self, node):
        if random.random() < self.input.pa:
            if node.channel_free:
                node.channel_free = self.check_channel_free(node)


            if node.channel_free and random.random() < self.input.pa:
                node.attempt = 1

                delay = self.generate_backoff(node.attempt, self.input.Tmax)

                if delay == 0:
                    node.state = NodeState.RTS
                    node.event_time = self.time + self.input.Trts
                    node.has_collision = False
                    node.channel_free = True
                else:
                    node.state = NodeState.BACKOFF
                    node.event_time = node.event_time + delay * self.input.Tbo
                    node.has_collision = False
                    node.channel_free = True
            else:
                node.state = NodeState.IDLE
                if node.channel_free:
                    node.event_time = self.time + self.input.Tidle
                else:
                    node.event_time = self.time + self.input.Tdata + self.input.Tack
                node.channel_free = True

    def serve_backoff(self, node):
        if node.channel_free:
            node.channel_free = self.check_channel_free(node)

        if node.channel_free:
            node.state = NodeState.RTS
            node.has_collision = False
            node.event_time = self.time + self.input.Trts
        else:
            node.state = NodeState.WAIT
            node.event_time = self.time + self.input.Twait
            
    def serve_rts(self, node):
        if not node.has_collision:
            node.has_collision = self.check_collisions(node)

        node.statistics.total_rts_count += 1.0

        if not node.has_collision:
            node.state = NodeState.CTS
            node.event_time = self.time + self.input.Tcts
        else:
            node.state = NodeState.OUT
            node.event_time = self.time + self.input.Tout
            node.statistics.collided_rts_count += 1.0

    def serve_out(self, node):
        if node.channel_free:
            node.channel_free = self.check_channel_free((node))

        if node.channel_free:
            node.attempt += 1

            if node.attempt <= self.input.Nretx + 1:
                delay = self.generate_backoff(node.attempt, self.input.Tmax)

                if delay == 0:
                    node.state = NodeState.RTS
                    node.event_time = self.time + self.input.Trts
                    node.has_collision = False
                    node.channel_free = True
                else:
                    node.state = NodeState.BACKOFF
                    node.event_time = node.event_time + delay * self.input.Tbo
                    node.has_collision = False
                    node.channel_free = True
            else:
                node.state = NodeState.IDLE
                node.event_time = self.time + self.input.Tidle
                node.attempt = 0
                node.channel_free = True
                node.has_collision = False

                node.statistics.failure_count += 1.0
        else:
            node.state = NodeState.OUT
            node.event_time = self.time + self.input.Tout
            node.channel_free = True

    def serve_cts(self, node):
        node.state = NodeState.DATA
        node.event_time = self.time + self.input.Tdata
        node.has_collision = False
        node.channel_free = True

    def serve_data(self, node):
        if not node.has_collision:
            node.has_collision = self.check_collisions(node)
        node.state = NodeState.ACK
        node.event_time = self.time + self.input.Tack

    def serve_ack(self, node):
        node.state = NodeState.IDLE
        node.event_time = self.time + self.input.Tidle
        node.attempt = 0
        node.channel_free = True
        node.has_collision = False

        node.statistics.success_count += 1.0

    def serve_wait(self, node):
        delay = self.generate_backoff_after_wait(node.attempt, self.input.Tmax)

        if delay == 0:
            node.state = NodeState.RTS
            node.event_time = self.time + self.input.Trts
            node.has_collision = False
            node.channel_free = True
        else:
            node.state = NodeState.BACKOFF
            node.event_time = node.event_time + delay * self.input.Tbo
            node.has_collision = False
            node.channel_free = True

    def generate_backoff(self, attempt, Tmax):
        return random.randrange(1, attempt * Tmax + 1)
    
    def generate_backoff_after_wait(self, attempt, Tmax):
        return random.randrange(0, attempt * Tmax + 1)

    def count_state_hits(self, node):
        node.statistics.slots_count += 1
        if node.state == NodeState.IDLE:
            node.statistics.idle_hits += 1
            node.statistics.cycles_count += 1
        elif node.state == NodeState.BACKOFF:
            node.statistics.backoff_hits += 1
        elif node.state == NodeState.RTS:
            node.statistics.rts_hits += 1
        elif node.state == NodeState.OUT:
            node.statistics.out_hits += 1
        elif node.state == NodeState.CTS:
            node.statistics.cts_hits += 1
        elif node.state == NodeState.WAIT:
            node.statistics.wait_hits += 1
        elif node.state == NodeState.DATA:
            node.statistics.data_hits += 1
        elif node.state == NodeState.ACK:
            node.statistics.ack_hits += 1

def print_to_csv_file(states, filename, results_folder):
    kwargs = {'newline': ''}
    mode = 'a'
    fname = 'results/' + results_folder + '/' + filename + '.csv'
    with open(fname, mode, **kwargs) as fp:
        writer = csv.writer(fp, delimiter=';')
        writer.writerow(states)


if __name__ == '__main__':
    main()
