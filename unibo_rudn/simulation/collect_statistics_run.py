import csv
import sys

import time

sys.path.append('../')

from unibo_rudn.core.simulation import Simulation


def main():
    start_time = time.time()

    enable_debug = False
    auto_continue = True
    nodes_number = 20
    maximum_allowed_radius = 10
    repeats = 1500

    # Node parameters
    T_max = 15
    rts_generation_intensity = 5
    t_out = 10
    retry_limit = 3
    # Gateway parameters
    rts_processing_duration = 1
    cts_channel_busy_time = 25 * rts_processing_duration

    statistics = {}

    for i in range(1, nodes_number+1):
        t1 = time.time()
        print("Simulation run for ", i,
              " Nodes distributed within a sphere with a radius", maximum_allowed_radius,
              ", repeats =", repeats)

        nodes = i
        collision_duration = 0
        collision_prob = 0
        time_before_channel_busy = 0
        nodes_count_that_transmitted_data = 0

        total_simulation_time = 0
        mean_sent_rts_count = 0

        for j in range(0, repeats):
            simulation = Simulation(i,
                                    maximum_allowed_radius,
                                    T_max,
                                    rts_generation_intensity,
                                    t_out,
                                    retry_limit,
                                    rts_processing_duration,
                                    cts_channel_busy_time,
                                    enable_debug,
                                    auto_continue)
            simulation.run()

            collision_duration += simulation.collision_duration
            collision_prob += simulation.collision_blocking_probability

            temp_time_before_channel_busy = 0
            temp_nodes_count_that_transmitted_data = 0
            temp_sent_rts = 0

            for node in simulation.nodes:
                temp_sent_rts += len(node.sent_rts_messages)
                if node.is_user_data_sent:
                    temp_nodes_count_that_transmitted_data += 1
                    if node.cts_message is not None:
                        temp_time_before_channel_busy += node.cts_message.arrived_to_node_at

            time_before_channel_busy += temp_time_before_channel_busy / len(simulation.nodes)
            nodes_count_that_transmitted_data += temp_nodes_count_that_transmitted_data / len(simulation.nodes)
            mean_sent_rts_count += temp_sent_rts / len(simulation.nodes)
            total_simulation_time += simulation.time

        total_simulation_time = total_simulation_time / repeats
        mean_sent_rts_count = mean_sent_rts_count / repeats

        time_before_channel_busy = time_before_channel_busy / repeats
        nodes_count_that_transmitted_data = nodes_count_that_transmitted_data / repeats

        collision_duration = collision_duration / repeats
        collision_prob = collision_prob / repeats

        statistics[nodes] = [nodes,
                             collision_duration,
                             collision_prob,
                             time_before_channel_busy,
                             nodes_count_that_transmitted_data,
                             total_simulation_time,
                             mean_sent_rts_count]
        t2 = time.time()
        print("     Executed in %s seconds" % (t2- t1))
    filename = "../simulation_results/nodes[" + str(1) + "-" + str(nodes_number) + "]_radius[" + str(maximum_allowed_radius) + "]_retry[" + str(retry_limit) + "].dat"
    kwargs = {'newline': ''}
    mode = 'w'
    with open(filename, mode, **kwargs) as fp:
        writer = csv.writer(fp, delimiter=' ')
        writer.writerow(["#nodes",
                         "collision time",
                         "collision probability",
                         "mean time before channel busy",
                         "mean number of node that transmitted data",
                         "total simulation time",
                         "mean sent rts count"])
        for keys, values in statistics.items():
            print(values)
            writer.writerow(values)


    end_time = time.time()
    print("Executed in %s seconds" % (end_time - start_time))


if __name__ == '__main__':
    main()
