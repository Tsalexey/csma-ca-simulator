import sys

from unibo_rudn.input.realistic_input1 import RealisticInput1

sys.path.append('../')

from unibo_rudn.core.simulation import Simulation


def main():
    data = RealisticInput1()
    sim = Simulation(data)
    sim.run()

    for node in sim.nodes:
        print("     node", node.id, ", collision:", node.stat_collision, ", success:", node.stat_success)

    print()
    print("hidden block: ", sim.gateway.stat_hidden_block)

    delta_data = data.tau_g_cts + data.tau_p_max + \
                 data.tau_g_data + data.tau_p_max + \
                 data.tau_g_ack + data.tau_p_max

    print()
    print("delta_data=", delta_data)
    print("tau_g_rts=", data.tau_g_rts)
    print()

    g_t = 0
    for node in sim.nodes:
        g_t += len(node.transmitted_rts_messages)

    print("number of generated calls by nodes =", g_t)
    print("total processed rts messages in GW =", len(sim.gateway.total_processed_rts_messages))
    print("number of correctly received calls in GW =", len(sim.gateway.successful_processed_rts_messages))
    print("number of not correctly received calls in GW =", len(sim.gateway.unsuccessful_processed_rts_messages))

    print()
    print("blocked rts / total rts")
    print("P{call1} =", len(sim.gateway.unsuccessful_processed_rts_messages), "/",
          len(sim.gateway.total_processed_rts_messages), "=",
          len(sim.gateway.unsuccessful_processed_rts_messages) / len(sim.gateway.total_processed_rts_messages))
    print()

    # print("all processed rts / potential number of RTS")
    # print("P{call2} =", len(sim.gateway.successful_processed_rts_messages)-sim.gateway.stat_hidden_block, "/",
    #       "=",
    #       (len(sim.gateway.successful_processed_rts_messages)-sim.gateway.stat_hidden_block) / (len(sim.nodes) * (data.N_retry+1)))
    # print()

    print("time of all rts processing / last ack time")
    print("P{time1} =", sim.gateway.total_working_time, "/",
          sim.gateway.last_ack_time, "=", sim.gateway.total_working_time / sim.gateway.last_ack_time)
    print()

    print("time of all rts processing / total gw working time")
    print("P{time2} =: ", sim.gateway.total_working_time, "/",
          sim.gateway.busy_time, "=", sim.gateway.total_working_time / sim.gateway.busy_time)
    print()

    # print("time for blocked / time for all processed")
    # print("P{time4} = ",
    #       data.tau_g_rts * len(sim.gateway.unsuccessful_processed_rts_messages), "/",
    #       (data.tau_g_rts * len(sim.gateway.total_processed_rts_messages)), "=",
    #       (data.tau_g_rts * len(sim.gateway.unsuccessful_processed_rts_messages)) / (
    #       data.tau_g_rts * len(sim.gateway.total_processed_rts_messages)))
    # print()


if __name__ == '__main__':
    main()
