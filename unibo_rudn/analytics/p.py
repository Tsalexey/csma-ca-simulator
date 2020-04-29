import csv
import time

from unibo_rudn.analytics.D_n_analytic import D_n_analytic
from unibo_rudn.core.simulation import Simulation
from unibo_rudn.input.realistic_input1 import RealisticInput1


def main():
    data = RealisticInput1()
    repeats = 500

    D_analytic = D_n_analytic(data, data.N_retry + 1).calculate()

    p_sim = {}
    p = {}

    for nodes in range(1, data.nodes_number + 1):


        t1 = time.time()
        print("Simulation run for ", nodes, " Nodes distributed within a sphere with a radius", data.sphere_radius,
              ", repeats =", repeats)

        p_temp = 0.0
        for j in range(0, repeats):
            data.nodes_number = nodes
            simulation = Simulation(data)
            simulation.run()
            p_temp += simulation.collision_time_blocking_probability
        p_sim[nodes] = p_temp / repeats
        t2 = time.time()
        print("     Executed in %s seconds" % (t2 - t1))


        sum = 0.0
        for i in range(1, data.N_retry + 1):
            sum += i / D_analytic[i]

        p[nodes] = 1 - pow(1 - data.tau_g_rts * sum, nodes - 1)

        filename = "../simulation_results/p_test_nodes[" + str(1) + "-" + str(nodes) + "]_radius[" + str(
            data.sphere_radius) + "]_retry[" + str(data.N_retry) + "].dat"
        kwargs = {'newline': ''}
        mode = 'w'

    with open(filename, mode, **kwargs) as fp:
        writer = csv.writer(fp, delimiter=' ')
        writer.writerow(["#nodes",
                         "p analytical",
                         "p simulation",
                         "1-p analytical"
                         ])
        for key, values in p_sim.items():
            writer.writerow([key,
                             p[key],
                             p_sim[key],
                             1 - p[key]
                             ])


if __name__ == '__main__':
    main()
