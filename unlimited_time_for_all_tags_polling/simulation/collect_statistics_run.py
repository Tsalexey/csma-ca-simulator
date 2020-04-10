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
    repeats = 50

    statistics = {}

    for i in range(1, nodes_number+1):
        t1 = time.time()
        print("Simulation run for ", i,
              " Nodes distributed within a sphere with a radius", maximum_allowed_radius,
              ", repeats =", repeats)

        nodes = i
        collision_duration = 0
        collision_prob = 0

        for j in range(0, repeats):
            simulation = Simulation(i, maximum_allowed_radius, enable_debug, auto_continue)
            simulation.run()

            collision_duration += simulation.collision_duration
            collision_prob += simulation.collision_blocking_probability

        collision_duration = collision_duration / repeats
        collision_prob = collision_prob / repeats

        statistics[nodes] = [nodes, collision_duration, collision_prob]
        t2 = time.time()
        print("     Executed in %s seconds" % (t2- t1))
    filename = "../simulation_results/nodes[" + str(1) + "-" + str(nodes_number) + "]_radius[" + str(maximum_allowed_radius) + "].dat"
    kwargs = {'newline': ''}
    mode = 'w'
    with open(filename, mode, **kwargs) as fp:
        writer = csv.writer(fp, delimiter=' ')
        writer.writerow(["#nodes", "collision time", "collision probability"])
        for keys, values in statistics.items():
            print(values)
            writer.writerow(values)

    statistics = {}

    tn=10
    for i in range(1, maximum_allowed_radius+1):
        t1 = time.time()
        print("Simulation run for ", tn,
              " Nodes distributed within a sphere with a radius", i,
              ", repeats =", repeats)

        radius = i
        collision_duration = 0
        collision_prob = 0

        for j in range(0, repeats):
            simulation = Simulation(tn, i, enable_debug, auto_continue)
            simulation.run()

            collision_duration += simulation.collision_duration
            collision_prob += simulation.collision_blocking_probability

        collision_duration = collision_duration / repeats
        collision_prob = collision_prob / repeats

        statistics[radius] = [radius, collision_duration, collision_prob]
        t2 = time.time()
        print("     Executed in %s seconds" % (t2- t1))

    filename = "../simulation_results/nodes[" + str(tn) + "]_radius[" + str(1) + "-" + str(maximum_allowed_radius) + "].dat"
    kwargs = {'newline': ''}
    mode = 'w'
    with open(filename, mode, **kwargs) as fp:
        writer = csv.writer(fp, delimiter=' ')
        writer.writerow(["#radius", "collision time", "collision probability"])
        for keys, values in statistics.items():
            print(values)
            writer.writerow(values)

    end_time = time.time()
    print("Executed in %s seconds" % (end_time - start_time))


if __name__ == '__main__':
    main()
