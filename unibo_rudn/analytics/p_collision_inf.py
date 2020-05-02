import csv
from functools import reduce

import time

from unibo_rudn.analytics.D_n_analytic import D_n_analytic
from unibo_rudn.core.simulation import Simulation
from unibo_rudn.input.realistic_input1 import RealisticInput1


def main():
    data = RealisticInput1()

    repeats = 50

    p_sim = {}
    p = {}
    p2 = {}

    upper_bound = data.N_retry
    if upper_bound is None:
        upper_bound = 5


    for node in range(1, data.nodes_number + 1):
        t1 = time.time()
        print("Simulation run for ", node, " Nodes distributed within a sphere with a radius", data.sphere_radius,
              ", repeats =", repeats)

        p_temp = 0.0

        for j in range(0, repeats):
            data.nodes_number = node
            simulation = Simulation(data)
            simulation.run()
            p_temp += simulation.collision_time_blocking_probability
        p_sim[node] = p_temp / repeats

        p_attempt = 1
        # p2_attempt = 1
        for attempt in range(1, upper_bound + 1):
        #     if node == 1 and attempt > 1:
        #         p_attempt.append(0)
        #         continue
            t = ((node - 1) * attempt * data.tau_g_rts + (attempt - 1) * data.tau_g_rts)
            # t2 = ((node - 1) * attempt * data.tau_g_rts + (attempt - 1) * data.tau_g_rts)
            p_attempt = p_attempt * (t/(data.tau_g_rts * node * attempt))
            # p_attempt.append(t / (data.tau_g_rts * node * attempt))
            # p2_attempt.append(t2 / (data.tau_g_rts * node * attempt))

        p[node] = p_attempt

        print("node", node)
        print(p[node])
        # p[node] = reduce(lambda x, y: x * y, p_attempt)
        # p2[node] = reduce(lambda x, y: x * y, p2_attempt)

        t2 = time.time()
        print("     Executed in %s seconds" % (t2 - t1))


    filename = "../simulation_results/p_collision_inf_nodes[" + str(1) + "-" + str(node) + "]_radius[" + str(
            data.sphere_radius) + "]_retry[" + str(data.N_retry) + "].dat"
    kwargs = {'newline': ''}
    mode = 'w'

    with open(filename, mode, **kwargs) as fp:
        writer = csv.writer(fp, delimiter=' ')
        writer.writerow(["#nodes",
                         "p analytical",
                         "p simulation",
                         ])
        for key, values in p.items():
            writer.writerow([key,
                             p[key],
                             p_sim[key],
                             # p2[key],
                             ])



if __name__ == '__main__':
    main()

