import sys

sys.path.append('../')

from allow_n_retries_at_gw.core.simulation import Simulation

def main():
    enable_debug = True
    nodes_number = 5
    maximum_allowed_radius = 10

    simulation = Simulation(nodes_number, maximum_allowed_radius, enable_debug)
    simulation.run()

if __name__ == '__main__':
    main()
