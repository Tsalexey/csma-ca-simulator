import csv
import sys
import time

from unibo_rudn.analytics.D_n_analytic import D_n_analytic
from unibo_rudn.core.node import get_tau_w
from unibo_rudn.core.simulation import Simulation
from unibo_rudn.input.realistic_input1 import RealisticInput1

sys.path.append('../')


def main():
    start_time = time.time()

    data = RealisticInput1()

    repeats = 500

    t1 = time.time()
    print("Simulation run for ", data.nodes_number, " Nodes distributed within a sphere with a radius",
          data.sphere_radius,
          ", repeats =", repeats)

    D_sim = {}
    D_sim_counter = {}

    for i in range(1, data.nodes_number + 1):
        t1 = time.time()
        print("Simulation run for ", i, " Nodes distributed within a sphere with a radius", data.sphere_radius,
              ", repeats =", repeats)

        for j in range(0, repeats):
            data.nodes_number = i
            simulation = Simulation(data)
            simulation.run()

            # statistics gathering
            for key in simulation.D_n.keys():
                if key in D_sim:
                    D_sim[key] += simulation.D_n[key]
                    D_sim_counter[key] += 1
                else:
                    D_sim[key] = simulation.D_n[key]
                    D_sim_counter[key] = 1
            t2 = time.time()
        print("     Executed in %s seconds" % (t2 - t1))

    for key in D_sim.keys():
        D_sim[key] = D_sim[key] / D_sim_counter[key]

    D_analytic = D_n_analytic(data, 25).calculate()

    filename = "../simulation_results/D_n_test_nodes[" + str(1) + "-" + str(data.nodes_number) + "]_radius[" + str(
        data.sphere_radius) + "]_retry[" + str(data.N_retry) + "].dat"
    kwargs = {'newline': ''}
    mode = 'w'
    with open(filename, mode, **kwargs) as fp:
        writer = csv.writer(fp, delimiter=' ')
        writer.writerow(["#retry",
                         "D(n) analytic",
                         "D(n) simulation"
                         ])
        for key, values in D_analytic.items():
            d_temp = '?'
            if key in D_sim:
                d_temp = D_sim[key]

            writer.writerow([key,
                             D_analytic[key],
                             d_temp
                             ])

    end_time = time.time()

    print("Executed in %s seconds" % (end_time - start_time))


if __name__ == '__main__':
    main()
