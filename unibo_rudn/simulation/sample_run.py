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
        print("         cycles:", node.cycles_count, ", P{success}=", node.cycle_p_success, ", E[Tc]=", node.cycle_E_tc, ", Tx RTS state time=", node.cycle_T_rts)

    print()
    print("hidden block: ", sim.gateway.stat_hidden_block)

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

    print("time of all rts processing / last ack time")
    print("P{time1} =", sim.gateway.total_working_time, "/",
          sim.gateway.last_ack_time, "=", sim.gateway.total_working_time / sim.gateway.last_ack_time)
    print()

    print("time of all rts processing / total gw working time")
    print("P{time2} =: ", sim.gateway.total_working_time, "/",
          sim.gateway.busy_time, "=", sim.gateway.total_working_time / sim.gateway.busy_time)
    print()

    print("E[Tc]=", sim.E_tc)
    print("P{success}=", sim.nodes_p_success)
    print("Time for Tx RTS state=", sim.T_rts)


if __name__ == '__main__':
    main()
