
import sys

from unibo_rudn.input.aloha_input import AlohaInput

sys.path.append("..")

import csv
from unibo_rudn.core.statistics_collector import StatisticCollector


def main():
    input = AlohaInput()

    collector = StatisticCollector(input)
    collector.run()

    output(input, "aloha_statisticts", collector.statistics, collector.statistics_description)
    output(input, "aloha_statistics_full", collector.detailed_statistics, collector.detailed_statistics_description)

def output(input, file_name, statistics, statistics_description):
    filename = "../results/" \
               + file_name \
               + "_pa[" + str(input.p_a) + "]" \
               + "_sensing[" + str(input.sensing) + "]" \
               + "_nodes[" + str(1) + "-" + str(input.NN) + "]" \
               + "_radius[" + str(input.sphere_radius) + "]" \
               + "_retry[" + str(input.Nretx) + "]" \
               + "_time[" + str(input.simulation_time) + "].csv"

    kwargs = {'newline': ''}
    mode = 'w'

    with open(filename, mode, **kwargs) as fp:
        writer = csv.writer(fp, delimiter=';')

        description = []
        for x in statistics_description.values():
            description.append(x)

        print(description)
        writer.writerow(description)

        for keys, values in statistics.items():
            print(values)
            writer.writerow(values)

    print()


if __name__ == '__main__':
    main()
