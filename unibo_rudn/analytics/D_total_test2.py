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

    D = {}
    D_total = {}
    p_tx_rts = {}
    p_success = {}

    # just limiting N_retry with a bug number because of summing to Inf is impossible
    if rts_retry is None:
        rts_retry = 2000

    tau_data = data.tau_p_max + data.tau_g_cts + data.tau_p_max + data.tau_g_data + data.tau_p_max + data.tau_g_ack

    # D_total depends on p_collision, p_collision depends on nodes number
    for i in range(1, data.nodes_number+1):

        D[i] = 0
        for n in range(1, rts_retry + 1):
            temp_tau = 0
            for m in range(1, n+1):
                if m > 1:
                    temp_tau += data.tau_out
                temp_tau += (get_tau_w(m, data.T_max) + data.tau_p_max + data.tau_g_rts)
            D[i] += (data.tau_p_max + temp_tau + tau_data) * ((pow(p[i], n-1) * (1 - p[i]))/(1-pow(p[i], rts_retry)))

        D_total[i] = D[i]

        temp_p_tx_rts = 1-p[i]

        for j in range(2, rts_retry):
            temp_p_tx_rts += j * pow(p[i], j-1) * (1-p[i])

        p_tx_rts[i] = (data.tau_g_rts * temp_p_tx_rts) / D_total[i]

        p_success[i] = 1 - pow(1-p_tx_rts[i], i-1)
        print("Retry:", data.N_retry, ", nodes:", i, ", d_total:", D_total[i])



    filename = "../simulation_results/D_total_test2_nodes[" + str(1) + "-" + str(data.nodes_number) + "]_radius[" + str(data.sphere_radius) + "]_retry[" + str(data.N_retry) + "].dat"
    kwargs = {'newline': ''}
    mode = 'w'
    with open(filename, mode, **kwargs) as fp:
        writer = csv.writer(fp, delimiter=' ')
        writer.writerow(["#nodes",
                         "collision probability",
                         "D_total",
                         "finished at (simulation)",
                         "p_tx_rts",
                         "p_success"])
        for key, values in p.items():
            writer.writerow([key,
                             p[key],
                             D_total[key],
                             finished_at[key],
                             p_tx_rts[key],
                             p_success[key]])

    end_time = time.time()
    print("Executed in %s seconds" % (end_time - start_time))


if __name__ == '__main__':
    main()
