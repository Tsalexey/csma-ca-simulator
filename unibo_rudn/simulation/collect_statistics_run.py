import csv
import sys
import time

from unibo_rudn.input.realistic_input1 import RealisticInput1

sys.path.append('../')

from unibo_rudn.core.simulation import Simulation


def main():
    start_time = time.time()

    input = RealisticInput1()
    repeats = 2500

    statistics = {}

    for i in range(1, input.nodes_number + 1):
        # if i % 10 != 0:
        #     continue

        t1 = time.time()
        print("Simulation run for ", i, " Nodes distributed within a sphere with a radius", input.sphere_radius,
              ", repeats =", repeats)

        nodes = i

        collision_by_time_prob = 0
        collision_by_call_prob = 0
        D_total = 0
        tau_data_divided_by_D_total = 0
        kpi_tau_data_divided_by_D_total = 0
        nodes_count_that_transmitted_data = 0

        number_of_generated_calls = 0
        number_of_correctly_received_calls = 0
        number_of_not_correctly_received_calls = 0
        number_of_calls_received_after_cts = 0

        transmitted_rts_messages = 0
        retransmitted_rts_messages = 0

        p_rts_collision_to_data = 0.0

        for j in range(0, repeats):
            input.nodes_number = i
            simulation = Simulation(input)
            simulation.run()

            # statistics gathering
            collision_by_time_prob += simulation.collision_time_blocking_probability
            collision_by_call_prob += simulation.collision_call_blocking_probability
            D_total += simulation.D_total
            tau_data_divided_by_D_total += simulation.tau_data_divided_by_D_total
            kpi_tau_data_divided_by_D_total += input.tau_g_data * simulation.tau_data_divided_by_D_total / input.T_beam
            nodes_count_that_transmitted_data += simulation.nodes_count_that_transmitted_data

            g_t = 0
            for node in simulation.nodes:
                g_t += len(node.transmitted_rts_messages)
            number_of_generated_calls += g_t
            number_of_correctly_received_calls += len(simulation.gateway.successful_processed_rts_messages)
            number_of_not_correctly_received_calls += len(simulation.gateway.unsuccessful_processed_rts_messages)
            number_of_calls_received_after_cts += len(simulation.gateway.rts_messages_to_be_processed)

            transmitted_rts_messages += simulation.transmitted_rts_messages
            retransmitted_rts_messages += simulation.retransmitted_rts_messages

            p_rts_collision_to_data += simulation.p_rts_collision_to_data

        collision_by_time_prob = collision_by_time_prob / repeats
        collision_by_call_prob = collision_by_call_prob / repeats
        D_total = D_total / repeats
        tau_data_divided_by_D_total = tau_data_divided_by_D_total / repeats
        kpi_tau_data_divided_by_D_total = kpi_tau_data_divided_by_D_total / repeats
        nodes_count_that_transmitted_data = nodes_count_that_transmitted_data / repeats

        number_of_generated_calls = number_of_generated_calls / repeats
        number_of_correctly_received_calls = number_of_correctly_received_calls / repeats
        number_of_not_correctly_received_calls = number_of_not_correctly_received_calls / repeats
        number_of_calls_received_after_cts = number_of_calls_received_after_cts / repeats

        transmitted_rts_messages = transmitted_rts_messages / repeats
        retransmitted_rts_messages = retransmitted_rts_messages / repeats

        statistics[nodes] = [nodes,
                             collision_by_time_prob,
                             collision_by_call_prob,
                             D_total,
                             nodes_count_that_transmitted_data,
                             tau_data_divided_by_D_total,
                             kpi_tau_data_divided_by_D_total,
                             number_of_generated_calls,
                             number_of_correctly_received_calls,
                             number_of_not_correctly_received_calls,
                             number_of_calls_received_after_cts,
                             transmitted_rts_messages,
                             retransmitted_rts_messages
                             ]
        t2 = time.time()
        print("     Executed in %s seconds" % (t2 - t1))
    filename = "../simulation_results/nodes[" + str(1) + "-" + str(input.nodes_number) + "]_radius[" + str(
        input.sphere_radius) + "]_retry[" + str(input.N_retry) + "].dat"
    kwargs = {'newline': ''}
    mode = 'w'
    with open(filename, mode, **kwargs) as fp:
        writer = csv.writer(fp, delimiter=' ')
        writer.writerow(["#nodes",
                         "collision by time",
                         "collision by call",
                         "collision by call on GW",
                         "D total",
                         "Nodes count that transmitted data",
                         "(tau_data / D_total) * (transmitted_nodes/all nodes)",
                         "1 - (tau_data / D_total) * (transmitted_nodes/all nodes)",
                         "number_of_generated_calls",
                         "number_of_correctly_received_calls",
                         "number_of_not_correctly_received_calls",
                         "transmitted_rts_messages",
                         "retransmitted_rts_messages"
                         ])
        for keys, values in statistics.items():
            print(values)
            writer.writerow(values)

    end_time = time.time()
    print("Executed in %s seconds" % (end_time - start_time))


if __name__ == '__main__':
    main()
