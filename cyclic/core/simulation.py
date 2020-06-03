import random

import numpy

from cyclic.core.gateway import Gateway, GatewayState
from cyclic.core.message import RTSMessage, CTSMessage
from cyclic.core.node import Node, NodeState
from unibo_rudn.core.simulation_type import SimulationType


class Simulation:
    def __init__(self, input):
        # input
        self.input = input

        # simulation parameters
        self.time = 0

        # gateway
        self.gateway = Gateway(self.input)

        # nodes
        self.nodes = []
        for i in range(1, self.input.nodes_number + 1):
            self.nodes.append(Node(i, self.input.sphere_radius, self.input))

    def run(self):
        """
        Run simulation
        """

        if self.input.is_debug:
            print("\n# Simulation started\n")

        while not self.is_simulation_finished():
            if self.input.is_debug:
                print("Time =", self.time, "is_simulation_finished:", self.is_simulation_finished())

            self.serve_nodes()
            self.serve_gateway()
            self.update_time()

            self.internal_debug()

        self.find_mean_node_statistic_values()
        self.find_gateway_statistic_values()

        if self.input.is_debug:
            print("\n# Simulation finished\n")

    def is_simulation_finished(self):
        if self.input.mode == SimulationType.ABSORBING:
            if self.input.N_retry is None:
                for node in self.nodes:
                    if node.state != NodeState.SUCCESS:
                        return False
            else:
                for node in self.nodes:
                    if node.state not in [NodeState.SUCCESS, NodeState.FAILURE]:
                        return False
            return True
        if self.input.mode == SimulationType.CYCLIC:
            return self.time > self.input.simulation_time

    def serve_nodes(self):
        for node in self.nodes:
            self.serve_node_idle(node)
            self.serve_node_backoff(node)
            self.serve_node_tx_rts(node)
            self.serve_node_out(node)
            self.serve_node_rx_cts(node)
            self.serve_node_wait(node)
            self.serve_node_tx_data(node)
            self.serve_node_success(node)
            self.serve_node_failure(node)

            if node.state not in list(map(lambda c: c, NodeState)):
                raise ValueError("Invalid state ", node.state, " for node", node.id)

    def serve_gateway(self):
        self.serve_gateway_tx_rts()
        self.serve_gateway_rx_data()

        if self.gateway.state not in list(map(lambda c: c, GatewayState)):
            raise ValueError("Invalid state ", self.gateway.state, " for gateway")


    def update_time(self):
        next_state = "None"

        min_node_event_time = None

        for node in self.nodes:
            if self.input.mode == SimulationType.ABSORBING and node.state in [NodeState.SUCCESS, NodeState.FAILURE]:
                continue
            if min_node_event_time is None and node.event_time is not None:
                min_node_event_time = node.event_time
            if node.event_time is not None and node.event_time < min_node_event_time:
                min_node_event_time = node.event_time

        if min_node_event_time is not None:
            event_time = min_node_event_time
            next_state = "Serve node"
        else:
            event_time = None
            next_state = "None"

        if self.gateway.state == GatewayState.RX_RTS:
            next_gw_rts = None
            if len(self.gateway.received_rts_messages) > 0:
                next_gw_rts = list(self.gateway.received_rts_messages.values())[0].reached_gateway_at
                for id, rts in self.gateway.received_rts_messages.items():
                    if rts.reached_gateway_at < next_gw_rts:
                        next_gw_rts = rts.reached_gateway_at

            if next_gw_rts is not None and next_gw_rts < event_time:
                event_time = next_gw_rts
                next_state = "Serve rts on gateway"

        if self.gateway.event_time is not None and self.gateway.event_time < event_time:
            event_time = self.gateway.event_time
            next_state = "Receive data on gateway"

        # if event_time is None:
        #     raise ValueError("Error at updating time, new time is None:", event_time)

        # if event_time == self.time:
        #     raise ValueError("Error at updating time, new time equal to previous:", event_time)

        # if event_time < self.time:
        #     raise ValueError("Error at updating time, new time less than previous:", event_time)

        if self.input.is_debug:
            print("New time: ", event_time, ", event:", next_state)

        self.time = event_time

    def serve_node_idle(self, node):
        """
            Check if node has RTS to transmit.
            If so, init transmission process
            Otherwise stay idle for some time
        """
        if node.event_time == self.time and node.state == NodeState.IDLE:
            if self.input.is_debug:
                print("     Node", node.id, ":", node.state.value, ", cycle ", node.cycle, ", attempt ", node.attempt)

            if node.cycle_start_time is None:
                node.cycle_start_time = self.time

            if random.random() < node.input.p_a:
                node.state = NodeState.BO
                node.cycle += 1
                node.attempt = 1
                node.event_time = self.time + numpy.random.uniform(0, node.attempt * self.input.T_max)

                if self.input.is_debug:
                    print("     Node", node.id, " goes to BACKOFF until", node.event_time)
            else:
                node.state = NodeState.IDLE
                node.event_time = self.time + self.input.tau_g_cts + self.input.tau_g_data + self.input.tau_g_ack

                if self.input.is_debug:
                    print("     Node", node.id, " keep staying IDLE")

    def serve_node_backoff(self, node):
        """
            After waiting back off window go to RTS transmission
        """
        if node.event_time == self.time and node.state == NodeState.BO:
            if self.input.is_debug:
                print("     Node", node.id, ":", node.state.value, ", cycle ", node.cycle, ", attempt ", node.attempt)

            node.state = NodeState.TX_RTS
            node.event_time = self.time + self.input.tau_g_rts

            if self.input.is_debug:
                print("     Node", node.id, " goes to TX RTS until", node.event_time)

    def serve_node_tx_rts(self, node):
        """
            Transmit RTS to gateway
        """
        if node.event_time == self.time and node.state == NodeState.TX_RTS:
            if self.input.is_debug:
                print("     Node", node.id, ":", node.state.value, ", cycle ", node.cycle, ", attempt ", node.attempt)

            node.statistics.rts_time += self.input.tau_g_rts

            node.state = NodeState.OUT
            node.event_time = self.time + self.input.tau_out

            rts_msg = RTSMessage(node.id)
            rts_msg.id = str(node.id) + "_" + str(self.time)
            rts_msg.reached_gateway_at = self.time + self.input.tau_g_rts + node.get_propagation_time()
            rts_msg.transmission_time = self.input.tau_g_rts
            rts_msg.propagation_time = node.get_propagation_time()

            self.gateway.received_rts_messages[rts_msg.id] = rts_msg

            if self.input.is_debug:
                print("     Node", node.id, "sent RTS, RTS arrive to gateway at", rts_msg.reached_gateway_at)
                print("     Node", node.id, "goes to OUT until", node.event_time)

    def serve_node_out(self, node):
        """
            No CTS were received.
            Go to the next attempt if attempts limit wasn't reached
            Go to failure state if attempt limit was reached
        """
        if node.event_time == self.time and node.state == NodeState.OUT:
            if self.input.is_debug:
                print("     Node", node.id, ":", node.state.value, ", cycle ", node.cycle, ", attempt ", node.attempt)

            if self.input.N_retry is None:
                node.state = NodeState.BO
                node.attempt += 1
                node.event_time = self.time + numpy.random.uniform(0, node.attempt * self.input.T_max)

                if self.input.is_debug:
                    print("     Node", node.id, " goes to BACKOFF #", node.attempt, "until", node.event_time)
            else:
                if node.attempt == self.input.N_retry + 1:
                    node.state = NodeState.FAILURE
                    node.event_time = self.time

                    if self.input.is_debug:
                        print("     Node", node.id, " goes to FAILURE in ", node.attempt, "attempt")
                else:
                    node.state = NodeState.BO
                    node.attempt += 1
                    node.event_time = self.time + numpy.random.uniform(0, node.attempt * self.input.T_max)

                    if self.input.is_debug:
                        print("     Node", node.id, " goes to BACKOFF #", node.attempt, "until", node.event_time)

    def serve_node_rx_cts(self, node):
        """
            If node receive CTS for other node, wait until end of transmission
            Else transmit data
        """
        if node.event_time == self.time and node.state == NodeState.RX_CTS:
            if self.input.is_debug:
                print("     Node", node.id, ":", node.state.value, ", cycle ", node.cycle, ", attempt ", node.attempt)

            if node.cts.node_id != node.id:
                node.state = NodeState.WAIT
                node.event_time = self.time \
                                    + self.input.tau_g_data \
                                    + self.input.tau_p_max \
                                    + self.input.tau_g_ack \
                                    + self.input.tau_p_max
                if self.input.is_debug:
                    print("     Node", node.id, " goes to WAIT because cts from ", node.cts.node_id, "until", node.event_time)
                node.cts = None
            else:
                node.cts = None
                node.state = NodeState.TX_DATA
                node.event_time = self.time \
                                  + self.input.tau_g_data \
                                  + node.get_propagation_time() \
                                  + self.input.tau_g_ack \
                                  + node.get_propagation_time()

                self.gateway.state = GatewayState.RX_DATA
                self.gateway.event_time = self.time \
                                  + self.input.tau_g_data \
                                  + node.get_propagation_time() \
                                  + self.input.tau_g_ack

                if self.input.is_debug:
                    print("     Node", node.id, " goes to TX DATA until", node.event_time)
                    print("     Gateway goes to RX DATA until", self.gateway.event_time)


    def serve_node_wait(self, node):
        if node.event_time == self.time and node.state == NodeState.WAIT:
            if self.input.is_debug:
                print("     Node", node.id, ":", node.state.value, ", cycle ", node.cycle, ", attempt ", node.attempt)

            node.state = NodeState.BO
            node.event_time = self.time + numpy.random.uniform(0, node.attempt * self.input.T_max)

            if self.input.is_debug:
                print("     Node", node.id, " goes to BACKOFF #", node.attempt, "until", node.event_time)

    def serve_node_tx_data(self, node):
        if node.event_time == self.time and node.state == NodeState.TX_DATA:
            if self.input.is_debug:
                print("     Node", node.id, ":", node.state.value, ", cycle ", node.cycle, ", attempt ", node.attempt)

            node.state = NodeState.SUCCESS
            node.event_time = self.time

            if self.input.is_debug:
                print("     Node", node.id, " goes to SUCCESS in ", node.attempt, "attempt")

    def serve_node_failure(self, node):
        """
            Terminate node activity for Absorbing mode
            Go to the next cycle for Cyclic mode
        """
        if node.event_time == self.time and node.state == NodeState.FAILURE:
            if self.input.is_debug:
                print("     Node", node.id, ":", node.state.value, ", cycle ", node.cycle, ", attempt ", node.attempt)

            node.cycle_end_time = self.time

            node.statistics.failure_count += 1
            node.statistics.cycle_time += node.cycle_end_time - node.cycle_start_time

            node.cycle_start_time = None
            node.cycle_end_time = None

            if self.input.mode == SimulationType.ABSORBING:
                node.state = NodeState.FAILURE
                node.event_time = None
            if self.input.mode == SimulationType.CYCLIC:
                node.state = NodeState.IDLE
                node.event_time = self.time + numpy.math.pow(10, -20)
            if self.input.mode not in list(map(lambda c: c, SimulationType)):
                raise ValueError("Unsupported simulation mode:", self.input.mode)

    def serve_node_success(self, node):
        """
            Terminate node activity for Absorbing mode
            Go to the next cycle for Cyclic mode
        """
        if node.event_time == self.time and node.state == NodeState.SUCCESS:
            if self.input.is_debug:
                print("     Node", node.id, ":", node.state.value, ", cycle ", node.cycle, ", attempt ", node.attempt)

            node.cycle_end_time = self.time

            node.statistics.success_count += 1
            node.statistics.cycle_time += node.cycle_end_time - node.cycle_start_time

            node.cycle_start_time = None
            node.cycle_end_time = None

            if self.input.mode == SimulationType.ABSORBING:
                node.state = NodeState.SUCCESS
                node.event_time = None
            if self.input.mode == SimulationType.CYCLIC:
                node.state = NodeState.IDLE
                node.event_time = self.time + numpy.math.pow(10, -20)
            if self.input.mode not in list(map(lambda c: c, SimulationType)):
                raise ValueError("Unsupported simulation mode:", self.input.mode)

    def serve_gateway_tx_rts(self):
        """
            Gateway listens channel for arriving RTS.
            If RTS arrive at current moment, check collisions
                1) In case of collision drop collided RTS
                2) In case of no collisions:
                    a) for sensing case send CTS for all nodes
                    b) for no sensing case send CTS only to single node
        """
        if self.gateway.state == GatewayState.RX_RTS:
            if self.input.is_debug:
                print("     Gateway", self.gateway.state, ", event time:", self.gateway.event_time)

            already_received_rts = []

            for id, rts in self.gateway.received_rts_messages.items():
                if rts.reached_gateway_at == self.time:
                    if self.input.is_debug:
                        print("     RTS from Node", rts.node_id, "reached gateway at", rts.reached_gateway_at)

                    already_received_rts.append(rts.id)
                    # check for collisions

                    collision_rts_list = []
                    collision_rts_ids = []
                    collision_ids = []

                    collision_start_time = rts.reached_gateway_at - rts.propagation_time
                    collision_end_time = rts.reached_gateway_at

                    for other_id, other_rts in self.gateway.received_rts_messages.items():
                        if rts.id != other_rts.id and rts.reached_gateway_at >= (other_rts.reached_gateway_at - other_rts.transmission_time):
                            if other_rts.id not in already_received_rts and other_rts.id not in collision_rts_ids:
                                collision_rts_list.append(other_rts)
                                collision_rts_ids.append(other_rts.id)
                                collision_ids.append(other_rts.id)

                    if collision_rts_list:
                        # we got collision
                        collision_rts_list.append(rts)
                        collision_rts_ids.append(rts.id)

                        for col in collision_rts_list:
                            self.gateway.statistics.received_rts += 1
                            self.gateway.statistics.blocked_rts += 1
                            already_received_rts.append(col.id)

                        if self.input.is_debug:
                            print("     There is a collision between", collision_rts_ids)
                    else:
                        # no collision, send CTS
                        if self.input.is_debug:
                            print("     There were no collisions")

                        self.gateway.statistics.received_rts += 1
                        self.gateway.statistics.not_blocked_rts += 1

                        for node in self.nodes:
                            # if node sensing is off, send CTS only to target node
                            if not self.input.sensing:
                                if rts.node_id != node.id:
                                    continue

                            cts_message = CTSMessage(rts.node_id)
                            cts_message.id = str(node.id) + "_" + str(self.time)
                            cts_message.reached_node_at = self.time + self.input.tau_g_cts + node.get_propagation_time()
                            cts_message.transmission_time = self.input.tau_g_cts
                            cts_message.propagation_time = node.get_propagation_time()

                            node.state = NodeState.RX_CTS
                            node.event_time = cts_message.reached_node_at
                            node.cts = cts_message

                            if self.input.is_debug:
                                print("     CTS sent to node", node.id, " and will reach it at", cts_message.reached_node_at)
            # remove served rts
            for rts_id in already_received_rts:
                self.gateway.received_rts_messages.pop(rts_id, None)

    def serve_gateway_rx_data(self):
        if self.gateway.state == GatewayState.RX_DATA and self.time == self.gateway.event_time:
            if self.input.is_debug:
                print("     Gateway", self.gateway.state, ", event time:", self.gateway.event_time)

            self.gateway.state = GatewayState.RX_RTS
            self.gateway.event_time = None

            received_during_data_transmission_rts = []

            for id, rts in self.gateway.received_rts_messages.items():
                if self.time > rts.reached_gateway_at:
                    received_during_data_transmission_rts.append(rts.id)

            for rts_id in received_during_data_transmission_rts:
                self.gateway.statistics.ignored_rts += 1
                self.gateway.received_rts_messages.pop(rts_id, None)

            if self.input.is_debug:
                print("     Gateway goes to RX RTS")

    def find_mean_node_statistic_values(self):
        for node in self.nodes:
            cycles_count = 1 if node.cycle == 0 else node.cycle
            node.statistics.total_cycle_count = node.cycle
            node.statistics.cycle_time = node.statistics.cycle_time / cycles_count
            node.statistics.rts_time = node.statistics.rts_time / cycles_count
            node.statistics.failure_count = node.statistics.failure_count / cycles_count
            node.statistics.success_count = node.statistics.success_count / cycles_count

    def find_gateway_statistic_values(self):
        self.gateway.statistics.received_rts += self.gateway.statistics.ignored_rts

        if self.gateway.statistics.received_rts == 0:
            self.gateway.statistics.blocking_probability_by_call = 0.0
        else:
            self.gateway.statistics.blocking_probability_by_call = (self.gateway.statistics.blocked_rts + self.gateway.statistics.ignored_rts) / self.gateway.statistics.received_rts

    def internal_debug(self):
        if self.input.is_debug and not self.input.auto_continue:
            print()
            user_input = input("[?] Press Enter in order to continue or input 'True' to enabled auto continue mode: ")
            if bool(user_input) == True:
                self.input.auto_continue = True

    def debug(self):
        print("Gateway:")
        print("     received rts:", self.gateway.statistics.received_rts)
        print("     blocked rts:", self.gateway.statistics.blocked_rts)
        print("     not blocked rts:", self.gateway.statistics.not_blocked_rts)
        print("     ignored rts:", self.gateway.statistics.ignored_rts)
        print("     Blocking probability by call:", self.gateway.statistics.blocking_probability_by_call)
        print("")
        for node in self.nodes:
            print("Node", node.id, ":", node.state.value)
            print("     total cycles:", node.statistics.total_cycle_count)
            print("     success:", node.statistics.success_count)
            print("     failure:", node.statistics.failure_count)
            print("     rts state time:", node.statistics.rts_time)
            print("     cycle time:", node.statistics.cycle_time)