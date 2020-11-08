
import sys

from unibo_rudn.input.aloha_input import AlohaInput

sys.path.append("..")

from unibo_rudn.core.statistics_collector import StatisticCollector, StatisticsType


def main():
    input = AlohaInput()

    collector = StatisticCollector(input)
    collector.run()
    collector.output(input, "aloha", StatisticsType.statistics)
    # collector.output(input, "aloha_detailed_statistics", StatisticsType.detailed_statistics)


if __name__ == '__main__':
    main()
