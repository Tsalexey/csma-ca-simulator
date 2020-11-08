
import sys
sys.path.append("..")

from unibo_rudn.core.statistics_collector import StatisticCollector, StatisticsType
from unibo_rudn.input.case2_input import Case2Input


def main():
    input = Case2Input()

    collector = StatisticCollector(input)
    collector.run()
    collector.output(input, "case2", StatisticsType.statistics)
    # collector.output(input, "case2_detailed_statistics", StatisticsType.detailed_statistics)


if __name__ == '__main__':
    main()
