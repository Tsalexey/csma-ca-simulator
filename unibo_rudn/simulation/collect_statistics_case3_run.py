
import sys



sys.path.append("..")

from unibo_rudn.core.statistics_collector import StatisticCollector, StatisticsType
from unibo_rudn.input.case3_input import Case3Input


def main():
    input = Case3Input()

    collector = StatisticCollector(input)
    collector.run()
    collector.output(input, "case3", StatisticsType.statistics)
    # collector.output(input, "case2_detailed_statistics", StatisticsType.detailed_statistics)


if __name__ == '__main__':
    main()
