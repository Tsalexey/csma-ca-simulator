import sys

import time

sys.path.append("..")

from unibo_rudn.core.simulation import Simulation
from unibo_rudn.input.case2_input import Case2Input

def main():
    data = Case2Input()

    start_time = time.time()

    sim = Simulation(data)
    sim.run()
    sim.debug()

    end_time = time.time()
    print("Executed in %s seconds" % (end_time - start_time))

if __name__ == '__main__':
    main()
