import csv
import sys

import time

sys.path.append('../')

from unlimited_time_for_all_tags_polling.core.simulation import Simulation


def main():
    start_time = time.time()

    enable_debug = False
    auto_continue = True
    nodes_number = 20
    maximum_allowed_radius = 10
    repeats = 500

    # Node parameters
    T_max = 15
    rts_generation_intensity = 5
    t_out = 10
    retry_limit = None
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

            for node in simulation.nodes:
                if node.cts_message is not None:
                    temp_time_before_channel_busy += node.cts_message.arrived_to_node_at
                if node.is_user_data_sent:
                    temp_nodes_count_that_transmitted_data += 1

            time_before_channel_busy += temp_time_before_channel_busy / len(simulation.nodes)
            nodes_count_that_transmitted_data += temp_nodes_count_that_transmitted_data / len(simulation.nodes)

        time_before_channel_busy = time_before_channel_busy / repeats
        nodes_count_that_transmitted_data = nodes_count_that_transmitted_data / repeats

        collision_duration = collision_duration / repeats
        collision_prob = collision_prob / repeats

        statistics[nodes] = [nodes, collision_duration, collision_prob, time_before_channel_busy, nodes_count_that_transmitted_data]
        t2 = time.time()
        print("     Executed in %s seconds" % (t2- t1))
    filename = "../simulation_results/nodes[" + str(1) + "-" + str(nodes_number) + "]_radius[" + str(maximum_allowed_radius) + "]_retry[" + str(retry_limit) + "].dat"
    kwargs = {'newline': ''}
    mode = 'w'
    with open(filename, mode, **kwargs) as fp:
        writer = csv.writer(fp, delimiter=' ')
        writer.writerow(["#nodes", "collision time", "collision probability", "mean time before channel busy", "mean number of node that transmitted data"])
        for keys, values in statistics.items():
            print(values)
            writer.writerow(values)

    statistics = {}

    # tn=10
    # for i in range(1, maximum_allowed_radius+1):
    #     t1 = time.time()
    #     print("Simulation run for ", tn,
    #           " Nodes distributed within a sphere with a radius", i,
    #           ", repeats =", repeats)
    #
    #     radius = i
    #     collision_duration = 0
    #     collision_prob = 0
    #
    #     for j in range(0, repeats):
    #         simulation = Simulation(tn,
    #                                 i,
    #                                 T_max,
    #                                 rts_generation_intensity,
    #                                 t_out,
    #                                 retry_limit,
    #                                 rts_processing_duration,
    #                                 cts_channel_busy_time,
    #                                 enable_debug,
    #                                 auto_continue)
    #         simulation.run()
    #
    #         collision_duration += simulation.collision_duration
    #         collision_prob += simulation.collision_blocking_probability
    #
    #     collision_duration = collision_duration / repeats
    #     collision_prob = collision_prob / repeats
    #
    #     statistics[radius] = [radius, collision_duration, collision_prob]
    #     t2 = time.time()
    #     print("     Executed in %s seconds" % (t2- t1))
    #
    # filename = "../simulation_results/nodes[" + str(tn) + "]_radius[" + str(1) + "-" + str(maximum_allowed_radius) + "].dat"
    # kwargs = {'newline': ''}
    # mode = 'w'
    # with open(filename, mode, **kwargs) as fp:
    #     writer = csv.writer(fp, delimiter=' ')
    #     writer.writerow(["#radius", "collision time", "collision probability"])
    #     for keys, values in statistics.items():
    #         print(values)
    #         writer.writerow(values)

    end_time = time.time()
    print("Executed in %s seconds" % (end_time - start_time))


if __name__ == '__main__':
    main()
