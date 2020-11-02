import sys

import time

from unibo_rudn_v2.input.aloha_input import AlohaInput

sys.path.append("..")

from unibo_rudn_v2.core.simulation import Simulation

def main():
    data = AlohaInput()

    start_time = time.time()

    sim = Simulation(data)
    sim.run()

    sim.print()

    end_time = time.time()
    print("Executed in %s seconds" % (end_time - start_time))

if __name__ == '__main__':
    main()
