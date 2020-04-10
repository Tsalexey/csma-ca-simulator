import sys

sys.path.append('../')

from unlimited_time_for_all_tags_polling.core.simulation import Simulation

def main():
    enable_debug = True
    auto_continue = True
    nodes_number = 20
    maximum_allowed_radius = 10

    simulation = Simulation(nodes_number, maximum_allowed_radius, enable_debug, auto_continue)
    simulation.run()

if __name__ == '__main__':
    main()
