from cyclic.core.simulation import Simulation
from unibo_rudn.input.input_discrete_time import InputDiscreteTime
from unibo_rudn.input.realistic_input1 import RealisticInput1


def main():
    data = InputDiscreteTime()
    sim = Simulation(data)
    sim.run()
    sim.debug()

if __name__ == '__main__':
    main()
