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
    repeats = 500

    # Node parameters
    T_max = 15
    rts_generation_intensity = 5
    t_out = 10
    retry_limit = 3
    # Gateway parameters
    rts_processing_duration = 1
    cts_channel_busy_time = 25 * rts_processing_duration

    gateway = Gateway(rts_processing_duration, cts_channel_busy_time, is_debug)

    nodes = []
    for i in range(1, nodes_number + 1):
        nodes.append(Node(i, nodes_number, T_max, rts_generation_intensity, t_out, retry_limit, is_debug))

    D_avg = {}
    p = {}

    D_1 = {}
    for node in nodes:
        D_1[node.id] = node.get_propagation_time() \
                       + node.get_tau_w(0, T_max) \
                       + node.get_tau_g_RTS(rts_generation_intensity) \
                       + node.get_propagation_time() \
                       + gateway.rts_processing_duration \
                       + node.get_propagation_time()

    for i in range(2, nodes_number + 1):
        t1 = time.time()
        print("Simulation run for ", i,
              " Nodes distributed within a sphere with a radius", maximum_allowed_radius,
              ", repeats =", repeats)

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
            collision_prob += simulation.collision_blocking_probability
        collision_prob = collision_prob / repeats

        p[i] = collision_prob

        sum_p = 0
        for n in range(0, retry_limit-1):
            sum_p += pow(p[i], n)

        D_1_avg = 0
        for k in range(2,i+1):
            D_1_avg += D_1[k]
            print("k=", k, "D_1_avg= ", D_1_avg)

        D_1_avg = D_1_avg / len(range(2,i+1))
        print("D_1_avg=", D_1_avg)

        print("     p=", p[i], ", sum p=", sum_p, ", D1_avg = ", D_1_avg)
        D_avg[i] = 0
        for n in range(1, retry_limit+1):
            sum_l = 0
            for l in range(0, n+1):
                sum_l += l
            D_avg[i] += D_avg[i] + pow(p[i], n-1)*(n*(t_out+rts_processing_duration)+(T_max/2)*sum_l)
            print("n=", n, ", D_avg = ", D_avg[i])
        D_avg[i] = D_avg[i] * (p[i]/sum_p)
        print("D_avg=", D_avg[i])
        D_avg[i] += D_1_avg
        print("D_avg=", D_avg[i])

        t2 = time.time()
        print("     Executed in %s seconds" % (t2 - t1))

    filename = "../simulation_results/analytical_overhead_nodes[" + str(1) + "-" + str(nodes_number) + "]_radius[" + str(maximum_allowed_radius) + "]_retry[" + str(retry_limit) + "].dat"
    kwargs = {'newline': ''}
    mode = 'w'
    with open(filename, mode, **kwargs) as fp:
        writer = csv.writer(fp, delimiter=' ')
        writer.writerow(["#nodes", "collision probability", "mean time before channel busy"])
        for i in range(1, nodes_number+1):
            if i == 1:
                writer.writerow([i, 0, D_1[i]])
            else:
                writer.writerow([i, p[i], D_avg[i]])

    end_time = time.time()
    print("Executed in %s seconds" % (end_time - start_time))

if __name__ == '__main__':
    main()