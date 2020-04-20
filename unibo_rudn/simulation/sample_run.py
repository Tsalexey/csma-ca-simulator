import sys

from unibo_rudn.input.realistic_input1 import RealisticInput1

sys.path.append('../')

from unibo_rudn.core.simulation import Simulation


def main():
    Simulation(RealisticInput1()).run()


if __name__ == '__main__':
    main()
