
import sys

from unibo_rudn.input.case3_refrain_input import Case3RefrainInput

sys.path.append("..")

from unibo_rudn.core.statistics_collector import StatisticCollector, StatisticsType

def main():
    input = Case3RefrainInput()

    collector = StatisticCollector(input)
    collector.run()
    collector.output(input, "case2", StatisticsType.statistics)
    # collector.output(input, "case2_detailed_statistics", StatisticsType.detailed_statistics)


if __name__ == '__main__':
    main()
