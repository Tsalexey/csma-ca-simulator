import csv
import os
import sys
import time
from datetime import datetime
import random
from enum import Enum
sys.path.append("..")

class Input:
    def __init__(self):
        self.simulation_time = 25000
        self.repeats = 25
        self.pa = 1.0
        self.start_from_NN = 1
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

        self.free_channel = 0.0
        self.busy_channel = 0.0
        self.channel = 0.0

        self.cycles_count = 0.0

class SimulationStatistics:
    def __init__(self):
        self.probability_of_collision = 0.0
        self.probability_of_success = 0.0
        self.probability_of_failure = 0.0
        self.probability_of_free_channel = 0.0
        self.probability_free_channel = 0.0
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
            single_measure = execute(temp_input, results_folder)
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
            summary.probability_free_channel += measure.probability_free_channel

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
        summary.probability_free_channel /= len(measures)

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


def execute(input, results_folder):
    """
    This function runs a single simulation for input parameters.
    Simulation stacktrace is saved to results_folder
    :param input: input configuration
    :param results_folder: folder where states history will be saved
    :return: statistics
    """
    # define nodes
    nodes = []
    history_description = ["Slot#"]
    for i in range(1, input.NN + 1):
        history_description.append("Node#{0}".format(i))
        node = Node(i)
        node.state = NodeState.IDLE
        node.event_time = input.Tidle
        nodes.append(node)

    print_to_csv_file(history_description, "states_history_{0}_nodes".format(input.NN), results_folder)

    time = 0
    while time <= input.simulation_time:

        prev_state = {}
        states = [time]

        for node in nodes:
            prev_state[node.id] = node.state
            states.append(node.state.value)
            count_state_hits(node)

        print_to_csv_file(states, "states_history_{0}_nodes".format(input.NN), results_folder)

        for node in nodes:

            if check_channel(node, nodes, prev_state):
                node.statistics.free_slots_count += 1
            else:
                node.statistics.busy_slots_count += 1

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
                        node.statistics.free_channel += 1
                        node.statistics.channel += 1
                    else:
                        node.state = NodeState.WAIT
                        node.event_time = time + input.Twait
                        node.statistics.busy_channel += 1
                        node.statistics.channel += 1
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
                        node.statistics.busy_channel += 1
                        node.statistics.channel += 1
                    else:
                        node.statistics.free_channel += 1
                        node.statistics.channel += 1
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

        simulation_statistics.probability_of_free_channel += node.statistics.free_slots_count / (node.statistics.free_slots_count + node.statistics.busy_slots_count)
        simulation_statistics.probability_free_channel += node.statistics.free_channel / (node.statistics.channel)

        simulation_statistics.probability_of_idle += node.statistics.idle_hits * input.Tslot / time
        simulation_statistics.probability_of_backoff += node.statistics.backoff_hits * input.Tslot / time
        simulation_statistics.probability_of_rts += node.statistics.rts_hits * input.Tslot / time
        simulation_statistics.probability_of_out += node.statistics.out_hits * input.Tslot / time
        simulation_statistics.probability_of_cts += node.statistics.cts_hits * input.Tslot / time
        simulation_statistics.probability_of_wait += node.statistics.wait_hits * input.Tslot / time
        simulation_statistics.probability_of_data += node.statistics.data_hits * input.Tslot / time
        simulation_statistics.probability_of_ack += node.statistics.ack_hits * input.Tslot / time

        simulation_statistics.time_of_cycle += time / node.statistics.cycles_count
        simulation_statistics.time_of_idle += node.statistics.idle_hits * input.Tslot / node.statistics.cycles_count
        simulation_statistics.time_of_backoff += node.statistics.backoff_hits * input.Tslot / node.statistics.cycles_count
        simulation_statistics.time_of_rts += node.statistics.rts_hits * input.Tslot / node.statistics.cycles_count
        simulation_statistics.time_of_out += node.statistics.out_hits * input.Tslot / node.statistics.cycles_count
        simulation_statistics.time_of_cts += node.statistics.cts_hits * input.Tslot / node.statistics.cycles_count
        simulation_statistics.time_of_wait += node.statistics.wait_hits * input.Tslot / node.statistics.cycles_count
        simulation_statistics.time_of_data += node.statistics.data_hits * input.Tslot / node.statistics.cycles_count
        simulation_statistics.time_of_ack += node.statistics.ack_hits * input.Tslot / node.statistics.cycles_count

    #normilize by nodes count

    simulation_statistics.probability_of_collision /= len(nodes)
    simulation_statistics.probability_of_success /= len(nodes)
    simulation_statistics.probability_of_failure /= len(nodes)
    simulation_statistics.probability_of_free_channel /= len(nodes)
    simulation_statistics.probability_free_channel /= len(nodes)

    simulation_statistics.probability_of_idle /= len(nodes)
    simulation_statistics.probability_of_backoff /= len(nodes)
    simulation_statistics.probability_of_rts /= len(nodes)
    simulation_statistics.probability_of_out /= len(nodes)
    simulation_statistics.probability_of_cts /= len(nodes)
    simulation_statistics.probability_of_wait /= len(nodes)
    simulation_statistics.probability_of_data /= len(nodes)
    simulation_statistics.probability_of_ack /= len(nodes)

    simulation_statistics.time_of_cycle /= len(nodes)
    simulation_statistics.time_of_idle /= len(nodes)
    simulation_statistics.time_of_backoff /= len(nodes)
    simulation_statistics.time_of_rts /= len(nodes)
    simulation_statistics.time_of_out /= len(nodes)
    simulation_statistics.time_of_cts /= len(nodes)
    simulation_statistics.time_of_wait /= len(nodes)
    simulation_statistics.time_of_data /= len(nodes)
    simulation_statistics.time_of_ack /= len(nodes)

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
    return random.randrange(1, attempt * Tmax + 1)

def generate_backoff_after_wait(attempt, Tmax):
    return random.randrange(0, attempt * Tmax + 1)

def count_state_hits(node):
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
    fname = 'results/' + results_folder + '/' + filename +'.csv'
    with open(fname, mode, **kwargs) as fp:
        writer = csv.writer(fp, delimiter=';')
        writer.writerow(states)

if __name__ == '__main__':
    main()
