
import sys
sys.path.append("..")

import csv
from unibo_rudn.core.statistics_collector import StatisticCollector
from unibo_rudn.input.realistic_input1 import RealisticInput1


def main():
    input = RealisticInput1()

    collector = StatisticCollector(input)
    collector.run()

    output(input, "statisticts", collector.statistics, collector.statistics_description)
    output(input, "statistics_full", collector.detailed_statistics, collector.detailed_statistics_description)

def output(input, file_name, statistics, statistics_description):
    filename = input.generate_output_filename(file_name)
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
