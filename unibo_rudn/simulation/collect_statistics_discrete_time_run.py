import csv
import sys

from unibo_rudn.core.statistics_collector import StatisticCollector
from unibo_rudn.input.input_discrete_time import InputDiscreteTime

sys.path.append('../')


def main():
    input = InputDiscreteTime()

    collector = StatisticCollector(input)
    collector.run()

    filename = "../results/discrete_" \
               + input.mode.value \
               + "_sensing[" + str(input.sensing) + "]" \
               + "_nodes[" + str(1) + "-" + str(input.NN) + "]" \
               + "_radius[" + str(input.sphere_radius) + "]" \
               + "_retry[" + str(input.Nretx) + "]_pa[" + str(input.p_a) + "]_time[" + str(input.simulation_time) + "].dat"

    kwargs = {'newline': ''}
    mode = 'w'

    with open(filename, mode, **kwargs) as fp:
        writer = csv.writer(fp, delimiter=' ')
        for keys, values in collector.statistics.items():
            print(values)
            writer.writerow(values)


if __name__ == '__main__':
    main()
