
import sys
sys.path.append("..")

import csv
from unibo_rudn.core.statistics_collector import StatisticCollector
from unibo_rudn.input.realistic_input1 import RealisticInput1


def main():
    input = RealisticInput1()

    collector = StatisticCollector(input)
    collector.run()

    filename = "../results/" \
               + input.mode.value \
               + "_sensing[" + str(input.sensing) + "]" \
               + "_nodes[" + str(1) + "-" + str(input.nodes_number) + "]" \
               + "_radius[" + str(input.sphere_radius) + "]" \
               + "_retry[" + str(input.N_retry) + "]_pa[" + str(input.p_a) + "].dat"

    kwargs = {'newline': ''}
    mode = 'w'

    with open(filename, mode, **kwargs) as fp:
        writer = csv.writer(fp, delimiter=' ')
        for keys, values in collector.statistics.items():
            print(values)
            writer.writerow(values)


if __name__ == '__main__':
    main()
