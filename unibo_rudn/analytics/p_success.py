import csv
import time

import numpy

from unibo_rudn.core.gateway import Gateway
from unibo_rudn.core.node import Node
from unibo_rudn.core.simulation import Simulation


def main():
    start_time = time.time()
    is_debug = False
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
        collision_prob = 0

        for j in range(0, repeats):
            simulation = Simulation(i,
                                    maximum_allowed_radius,
                                    T_max,
                                    rts_generation_intensity,
                                    t_out,
                                    retry_limit,
                                    rts_processing_duration,
                                    cts_channel_busy_time,
                                    is_debug,
                                    auto_continue)
            simulation.run()
            collision_prob += simulation.collision_time_blocking_probability
        collision_prob = collision_prob / repeats

        statistics[nodes] = [nodes,
                             collision_prob]
        t2 = time.time()
        print("     Executed in %s seconds" % (t2- t1))


    for key, value in statistics.items():
        p_success = 1 - pow(value[1], retry_limit)
        value.append(p_success)

    filename = "../simulation_results/analytical_p_success_nodes[" + str(1) + "-" + str(nodes_number) + "]_radius[" + str(maximum_allowed_radius) + "]_retry[" + str(retry_limit) + "].dat"
    kwargs = {'newline': ''}
    mode = 'w'
    with open(filename, mode, **kwargs) as fp:
        writer = csv.writer(fp, delimiter=' ')
        writer.writerow(["#nodes",
                         "collision probability",
                         "p{success}"])
        for keys, values in statistics.items():
            print(values)
            writer.writerow(values)

    end_time = time.time()
    print("Executed in %s seconds" % (end_time - start_time))

if __name__ == '__main__':
    main()