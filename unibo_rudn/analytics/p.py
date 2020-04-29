import csv
import time

from unibo_rudn.core.node import get_tau_w
from unibo_rudn.input.realistic_input1 import RealisticInput1


def main():
    start_time = time.time()

    data = RealisticInput1()

    N = data.N_retry

    if N is None:
        N = 2000

    p = {}
    p_chiara = {}

    p_tx = {}
    p_tx_chiara = {}

    D_1 = data.tau_p_max + get_tau_w(1,
                                     data.T_max) + data.tau_g_rts + data.tau_p_max + data.tau_g_cts + data.tau_p_max + data.tau_g_data + data.tau_p_max + data.tau_g_ack + data.tau_p_max

    for i in range(1, data.nodes_number + 1):
        print("Nodes", i)
        sum = 0.0
        sum_chiara = 0.0

        for n in range(1, N + 1 + 1):
            sum_t_w = 0.0

            for m in range(1, n + 1):
                sum_t_w += (m * data.T_max) / 2 #get_tau_w(m, data.T_max)

            sum += (n) / (data.tau_p_max
                          + (n - 1) * data.tau_out
                          + n * (data.tau_g_rts + data.tau_p_max)
                          + sum_t_w
                          + data.tau_g_cts
                          + data.tau_p_max
                          + data.tau_g_data
                          + data.tau_p_max
                          + data.tau_g_ack
                          + data.tau_p_max)

            sum_chiara += (D_1 + n * (data.tau_out + data.tau_g_rts) + sum_t_w)

        p_tx[i] = sum
        p_tx_chiara[i] = sum_chiara

        p[i] = 1 - pow(1 - data.tau_g_rts * p_tx[i], data.nodes_number - 1)
        p_chiara[i] = 1 - pow(1 - data.tau_g_rts * p_tx_chiara[i], data.nodes_number - 1)

    filename = "../simulation_results/p_test_nodes[" + str(1) + "-" + str(data.nodes_number) + "]_radius[" + str(
        data.sphere_radius) + "]_retry[" + str(data.N_retry) + "].dat"
    kwargs = {'newline': ''}
    mode = 'w'
    with open(filename, mode, **kwargs) as fp:
        writer = csv.writer(fp, delimiter=' ')
        writer.writerow(["#nodes",
                         "p",
                         "p_tx",
                         "p_chiara",
                         "p_tx_chiara"])
        for key, values in p.items():
            writer.writerow([key,
                             p[key],
                             p_tx[key],
                             p_chiara[key],
                             p_tx_chiara[key]])

    end_time = time.time()
    print("Executed in %s seconds" % (end_time - start_time))


if __name__ == '__main__':
    main()
