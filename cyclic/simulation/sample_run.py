import sys
sys.path.append("..")

from cyclic.core.simulation import Simulation
from cyclic.core.statistics_collector import StatisticCollector
from unibo_rudn.input.realistic_input1 import RealisticInput1

def main():
    data = RealisticInput1()

    # collector = StatisticCollector(data)
    # collector.run()
    # collector.debug()
    sim = Simulation(data)
    sim.run()
    sim.debug()

if __name__ == '__main__':
    main()
