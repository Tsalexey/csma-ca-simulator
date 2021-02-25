import csv
import os
import sys
from datetime import datetime
import random
from enum import Enum
sys.path.append("..")

class Input:
    def __init__(self):
        self.simulation_time = 10000
        self.repeats = 50
        self.pa = 1.0
        self.NN = 10
        self.Nretx = 3
        self.Tslot = 3
        self.Tidle = 3
        self.Trts = 3
        self.Tcts = 3
        self.Tbo = 3
        self.Tdata = 30
        self.Tack = 3
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

class SimulationStatistics:
    def __init__(self):
        self.probability_of_collision = 0.0
        self.probability_of_success = 0.0
        self.probability_of_failure = 0.0

def main():
    results_folder = datetime.now().strftime('%Y.%m.%d_%H-%M-%S')
    if not os.path.exists('results/' + results_folder):
        os.makedirs('results/' + results_folder)

    print("Results will be stored in " + results_folder)
    print("Simulation in progress")

    input = Input()

    for k,v in vars(input).items():
        print_to_csv_file([k, v], "input_parameters", results_folder)

    measures = []
    for i in range(1, input.repeats + 1):
        print("Node {0}/{1}, Scenario {2}/{3}".format(input.NN, input.NN, i, input.repeats))
        measures.append(execute(input, results_folder))

    summary = SimulationStatistics()

    for measure in measures:
        summary.probability_of_collision += measure.probability_of_collision
        summary.probability_of_failure += measure.probability_of_failure
        summary.probability_of_success += measure.probability_of_success

    summary.probability_of_collision /= len(measures)
    summary.probability_of_failure /= len(measures)
    summary.probability_of_success /= len(measures)

    for k, v in vars(summary).items():
        print(k + " - " + str(v))

def execute(input, results_folder):
    nodes = []
    for i in range(1, input.NN + 1):
        node = Node(i)
        node.state = NodeState.IDLE
        node.event_time = input.Tidle
        nodes.append(node)

    state_history = []

    time = 0
    while time <= input.simulation_time:

        prev_state = {}
        states = [time]

        for node in nodes:
            prev_state[node.id] = node.state
            states.append(node.state.value)

        print_to_csv_file(states, "states_history", results_folder)

        for node in nodes:
            if time == node.event_time:
                # IDLE state
                if node.state == NodeState.IDLE:
                    if random.random() < input.pa:
                        node.attempt = 1

                        delay = generate_backoff(node.attempt, input.Tmax)

                        if delay == 0:
                            node.state = NodeState.RTS
                            node.event_time = time + input.Trts
                            node.has_collision = False
                            node.channel_free = True
                        else:
                            node.state = NodeState.BACKOFF
                            node.event_time = node.event_time + delay * input.Tbo
                            node.has_collision = False
                            node.channel_free = True

                    else:
                        node.state = NodeState.IDLE
                        node.event_time = time + input.Tidle
                #  BACKOFF state
                elif node.state == NodeState.BACKOFF:
                    if node.channel_free:
                        node.channel_free = check_channel(node, nodes, prev_state)

                    if node.channel_free:
                        node.state = NodeState.RTS
                        node.has_collision = False
                        node.event_time = time + input.Trts
                    else:
                        node.state = NodeState.WAIT
                        node.event_time = time + input.Twait
                # RTS state
                elif node.state == NodeState.RTS:
                    if not node.has_collision:
                        node.has_collision = check_collision(node, nodes, prev_state)

                    node.statistics.total_rts_count += 1.0

                    if not node.has_collision:
                        node.state = NodeState.CTS
                        node.event_time = time + input.Tcts

                        node.statistics.not_collided_rts_count += 1.0
                    else:
                        node.state = NodeState.OUT
                        node.event_time = time + input.Tout

                        node.statistics.collided_rts_count += 1.0
                # OUT state
                elif node.state == NodeState.OUT:
                    if node.channel_free:
                        node.channel_free = check_channel(node, nodes, prev_state)

                    if node.channel_free:
                        node.attempt += 1

                        if node.attempt <= input.Nretx + 1:
                            delay = generate_backoff(node.attempt, input.Tmax)

                            if delay == 0:
                                node.state = NodeState.RTS
                                node.event_time = time + input.Trts
                                node.has_collision = False
                                node.channel_free = True
                            else:
                                node.state = NodeState.BACKOFF
                                node.event_time = node.event_time + delay * input.Tbo
                                node.has_collision = False
                                node.channel_free = True
                        else:
                            node.state = NodeState.IDLE
                            node.event_time = time + input.Tidle
                            node.attempt = 0
                            node.channel_free = True
                            node.has_collision = False

                            node.statistics.failure_count += 1.0
                    else:
                        node.state = NodeState.OUT
                        node.event_time = time + input.Tout
                        node.channel_free = True
                # CTS state
                elif node.state == NodeState.CTS:
                    node.state = NodeState.DATA
                    node.event_time = time + input.Tdata
                    node.has_collision = False
                    node.channel_free = True
                # DATA state
                elif node.state == NodeState.DATA:
                    if not node.has_collision:
                        node.has_collision = check_collision(node, nodes, prev_state)
                    node.state = NodeState.ACK
                    node.event_time = time + input.Tack
                # ACK state
                elif node.state == NodeState.ACK:
                    node.state = NodeState.IDLE
                    node.event_time = time + input.Tidle
                    node.attempt = 0
                    node.channel_free = True
                    node.has_collision = False

                    node.statistics.success_count += 1.0
                #  WAIT state
                elif node.state == NodeState.WAIT:
                    delay = generate_backoff_after_wait(node.attempt, input.Tmax)

                    if delay == 0:
                        node.state = NodeState.RTS
                        node.event_time = time + input.Trts
                        node.has_collision = False
                        node.channel_free = True
                    else:
                        node.state = NodeState.BACKOFF
                        node.event_time = node.event_time + delay * input.Tbo
                        node.has_collision = False
                        node.channel_free = True
            else:
                # RTS
                if node.state == NodeState.RTS:
                    if not node.has_collision:
                        node.has_collision = check_collision(node, nodes, prev_state)
                # BACKOFF
                elif node.state == NodeState.BACKOFF:
                    if node.channel_free:
                        node.channel_free = check_channel(node, nodes, prev_state)

                    if not node.channel_free:
                        node.state = NodeState.WAIT
                        node.event_time = time + input.Twait
                        node.channel_free = True
                        node.has_collision = False
                # OUT
                elif node.state == NodeState.OUT:
                    if node.channel_free:
                        node.channel_free = check_channel(node, nodes, prev_state)

                    if not node.channel_free:
                        node.state = NodeState.OUT
                        node.event_time = time + input.Tcts
                        node.channel_free = False
                        node.has_collision = False
                # DATA
                elif node.state == NodeState.DATA:
                    if not node.has_collision:
                        node.has_collision = check_collision(node, nodes, prev_state)

        time += input.Tslot

    # simulation finished, calculate statistics
    simulation_statistics = SimulationStatistics()

    for node in nodes:
        simulation_statistics.probability_of_collision += node.statistics.collided_rts_count / node.statistics.total_rts_count
        simulation_statistics.probability_of_success += node.statistics.success_count / (node.statistics.success_count + node.statistics.failure_count)
        simulation_statistics.probability_of_failure += node.statistics.failure_count / (node.statistics.success_count + node.statistics.failure_count)

    simulation_statistics.probability_of_collision /= len(nodes)
    simulation_statistics.probability_of_success /= len(nodes)
    simulation_statistics.probability_of_failure /= len(nodes)

    return simulation_statistics

def check_collision(node, nodes, prev_state):
    for another_node in nodes:
        if node.id != another_node.id and prev_state[another_node.id] in [NodeState.RTS, NodeState.CTS, NodeState.DATA]:
            return True
    return False

def check_channel(node, nodes, prev_state):
    for another_node in nodes:
        if node.id != another_node.id and prev_state[another_node.id] == NodeState.CTS:
            return False
    return True

def generate_backoff(attempt, Tmax):
    return random.randrange(1, attempt * Tmax)

def generate_backoff_after_wait(attempt, Tmax):
    return random.randrange(0, attempt * Tmax)

def print_to_csv_file(states, filename, results_folder):
    kwargs = {'newline': ''}
    mode = 'a'
    fname = 'results/' + results_folder + '/' + filename +'.csv'
    with open(fname, mode, **kwargs) as fp:
        writer = csv.writer(fp, delimiter=';')
        writer.writerow(states)

if __name__ == '__main__':
    main()
