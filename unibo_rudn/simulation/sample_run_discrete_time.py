import sys

from unibo_rudn.core.statistics_collector import StatisticCollector
from unibo_rudn.input.input_discrete_time import InputDiscreteTime

sys.path.append('../')

def main():
    data = InputDiscreteTime()
    collector = StatisticCollector(data)
    collector.run()
    collector.debug()

    # sim = Simulation(data)
    # sim.run()
    # sim.debug()

if __name__ == '__main__':
    main()
