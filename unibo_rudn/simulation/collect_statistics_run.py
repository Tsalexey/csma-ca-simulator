import csv
import sys

import time

from unibo_rudn.input.realistic_input1 import RealisticInput1

sys.path.append('../')

from unibo_rudn.core.simulation import Simulation


def main():
    start_time = time.time()

    input = RealisticInput1()
    repeats = 1000

    statistics = {}

    for i in range(1, input.nodes_number+1):
        t1 = time.time()
        print("Simulation run for ", i, " Nodes distributed within a sphere with a radius", input.sphere_radius, ", repeats =", repeats)

        nodes = i
        collision_duration = 0
        collision_prob = 0
        time_before_channel_busy = 0
        nodes_count_that_transmitted_data = 0
        total_simulation_time = 0
        mean_sent_rts_count = 0

        D_ave_with_tau_data = 0
        ratio_tau_data_to_D_ave_plus_tau_data = 0

        for j in range(0, repeats):
            input.nodes_number = i
            simulation = Simulation(input)
            simulation.run()

            # statistics gathering
            collision_duration += simulation.collision_duration
            collision_prob += simulation.collision_blocking_probability
            total_simulation_time += simulation.time
            time_before_channel_busy += simulation.time_before_channel_busy
            nodes_count_that_transmitted_data += simulation.nodes_count_that_transmitted_data
            mean_sent_rts_count += simulation.mean_sent_rts_count
            D_ave_with_tau_data += simulation.time_before_channel_busy + input.tau_g_data

        total_simulation_time = total_simulation_time / repeats
        collision_duration = collision_duration / repeats
        collision_prob = collision_prob / repeats
        mean_sent_rts_count = mean_sent_rts_count / repeats
        time_before_channel_busy = time_before_channel_busy / repeats
        nodes_count_that_transmitted_data = nodes_count_that_transmitted_data / repeats
        D_ave_with_tau_data = D_ave_with_tau_data / repeats
        ratio_tau_data_to_D_ave_plus_tau_data = input.tau_g_data / D_ave_with_tau_data

        statistics[nodes] = [nodes,
                             collision_duration,
                             collision_prob,
                             time_before_channel_busy,
                             nodes_count_that_transmitted_data,
                             total_simulation_time,
                             mean_sent_rts_count,
                             D_ave_with_tau_data,
                             ratio_tau_data_to_D_ave_plus_tau_data]
        t2 = time.time()
        print("     Executed in %s seconds" % (t2- t1))
    filename = "../simulation_results/nodes[" + str(1) + "-" + str(input.nodes_number) + "]_radius[" + str(input.sphere_radius) + "]_retry[" + str(input.N_retry) + "].dat"
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
                         "mean sent rts count,"
                         "D_ave + tau_data",
                         "tau_data/(D_ave+tau_data)"])
        for keys, values in statistics.items():
            print(values)
            writer.writerow(values)

    end_time = time.time()
    print("Executed in %s seconds" % (end_time - start_time))


if __name__ == '__main__':
    main()
