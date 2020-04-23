import csv
import sys
import time

from unibo_rudn.core.node import get_tau_w
from unibo_rudn.input.realistic_input1 import RealisticInput1

sys.path.append('../')

from unibo_rudn.core.simulation import Simulation


def main():
    start_time = time.time()

    data = RealisticInput1()

    repeats = 1000

    rts_retry = data.N_retry

    p = {}
    finished_at = {}

    for i in range(1, data.nodes_number+1):
        t1 = time.time()
        print("Simulation run for ", i, " Nodes distributed within a sphere with a radius", data.sphere_radius,
              ", repeats =", repeats)

        nodes = i
        collision_prob = 0
        mean_node_finished_at = 0

        for j in range(0, repeats):
            data.nodes_number = i
            simulation = Simulation(data)
            simulation.run()

            # statistics gathering
            collision_prob += simulation.collision_time_blocking_probability
            mean_node_finished_at += simulation.mean_node_finished_at

        collision_prob = collision_prob / repeats
        mean_node_finished_at = mean_node_finished_at / repeats

        p[nodes] = collision_prob
        finished_at[nodes] = mean_node_finished_at

        t2 = time.time()
        print("     Executed in %s seconds" % (t2 - t1))

    D_1 = data.tau_p_max + get_tau_w(0,
                                     data.T_max) + data.tau_g_rts + data.tau_p_max + data.tau_g_cts + data.tau_p_max + data.tau_g_data + data.tau_p_max + data.tau_g_ack + data.tau_p_max

    D_total = {}
    D_total_normalized = {}
    p_tx_rts = {}
    p_tx_rts_normalized = {}
    p_success = {}
    p_succedd_mormalized = {}

    # just limiting N_retry with a bug number because of summing to Inf is impossible
    if rts_retry is None:
        rts_retry = 2000

    # D_total depends on p_collision, p_collision depends on nodes number
    for i in range(1, data.nodes_number+1):
        D_total[i] = D_1 * (1 - p[i])
        D_total_normalized[i] = D_1 * ((1 - p[i]) / (1 - pow(p[i], rts_retry)))

        temp = 0.0
        temp_normalized = 0.0
        for n in range(1, rts_retry + 1):
            sum_t_w = 0.0
            for m in range(1, n):
                sum_t_w += get_tau_w(m, data.T_max)

            temp += (D_1 + n * (data.tau_out + data.tau_g_rts) + sum_t_w) * pow(p[i], n) * (1 - p[i])
            temp_normalized += (D_1 + n * (data.tau_out + data.tau_g_rts) + sum_t_w) * ((
                                                                                            pow(p[i], n) * (
                                                                                                1 - p[i])) / (
                                                                                            1 - pow(p[i], rts_retry)))

        D_total[i] += temp
        D_total_normalized[i] += temp_normalized

        temp_p_tx_rts = 1-p[i]
        temp_p_tx_rts_normalized = 1 - p[i]

        for j in range(2, rts_retry):
            temp_p_tx_rts += j * pow(p[i], j-1) * (1-p[i])
            temp_p_tx_rts_normalized += j * pow(p[i], j-1) * (1-p[i])

        p_tx_rts[i] = (data.tau_g_rts * temp_p_tx_rts) / D_total[i]
        p_tx_rts_normalized[i] = (data.tau_g_rts * temp_p_tx_rts_normalized) / D_total_normalized[i]

        p_success[i] = 1 - pow(1-p_tx_rts[i], i-1)
        p_succedd_mormalized[i] = 1 - pow(1-p_tx_rts_normalized[i], i-1)
        print("Retry:", data.N_retry, ", nodes:", i, ", d_total:", D_total[i], ", d_total_normalized:", D_total_normalized[i])



    filename = "../simulation_results/D_total_test_nodes[" + str(1) + "-" + str(data.nodes_number) + "]_radius[" + str(data.sphere_radius) + "]_retry[" + str(data.N_retry) + "].dat"
    kwargs = {'newline': ''}
    mode = 'w'
    with open(filename, mode, **kwargs) as fp:
        writer = csv.writer(fp, delimiter=' ')
        writer.writerow(["#nodes",
                         "collision probability",
                         "D_total",
                         "finished at (simulation)",
                         "D_total_normilized",
                         "p_tx_rts",
                         "p_tx_rts_normalized",
                         "p_success",
                         "p_success_normalized"])
        for key, values in p.items():
            writer.writerow([key,
                             p[key],
                             D_total[key],
                             finished_at[key],
                             D_total_normalized[key],
                             p_tx_rts[key],
                             p_tx_rts_normalized[key],
                             p_success[key],
                             p_succedd_mormalized[key]])

    end_time = time.time()
    print("Executed in %s seconds" % (end_time - start_time))


if __name__ == '__main__':
    main()
