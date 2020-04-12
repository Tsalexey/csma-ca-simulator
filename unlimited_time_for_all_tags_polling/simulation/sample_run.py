import sys

sys.path.append('../')

from unlimited_time_for_all_tags_polling.core.simulation import Simulation

def main():
    enable_debug = True
    auto_continue = True
    nodes_number = 20
    maximum_allowed_radius = 10

    # Node parameters
    T_max = 15
    rts_generation_intensity = 5
    t_out = 10
    retry_limit = 3
    # Gateway parameters
    rts_processing_duration = 1
    cts_channel_busy_time = 25 * rts_processing_duration

    simulation = Simulation(nodes_number,
                            maximum_allowed_radius,
                            T_max,
                            rts_generation_intensity,
                            t_out,
                            retry_limit,
                            rts_processing_duration,
                            cts_channel_busy_time,
                            enable_debug,
                            auto_continue)
    simulation.run()

if __name__ == '__main__':
    main()
