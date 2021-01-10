import sys

import time

from unibo_rudn.input.case3_refrain_input import Case3RefrainInput

sys.path.append("..")

from unibo_rudn.core.simulation import Simulation

def main():
    data = Case3RefrainInput()

    start_time = time.time()

    sim = Simulation(data)
    sim.run()
    sim.debug()

    end_time = time.time()
    print("Executed in %s seconds" % (end_time - start_time))

if __name__ == '__main__':
    main()
