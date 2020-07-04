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
        self.iter_counter = 0

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

            self.validate_run()

            self.serve_nodes()
            self.serve_gateway()
            self.update_time()

            self.internal_debug()

        self.find_mean_node_statistic_values()
        self.find_gateway_statistic_values()

        if self.input.is_debug:
            print("\n# Simulation finished\n")

    def is_simulation_finished(self):
        self.iter_counter +=1
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
            if self.input.time_limit == True:
                return self.time > self.input.simulation_time
            else:
                if len(self.nodes) > 1:
                    for i in self.nodes:
                        for j in self.nodes:
                            if i == j:
                                continue

                            if i.cycle == 0 or j.cycle == 0:
                                return False

                            etc_i = i.statistics.cycle_time2 / i.cycle
                            etc_j = j.statistics.cycle_time2 / j.cycle

                            if etc_i == 0 or etc_j == 0:
                                return False

                            error = abs(etc_i - etc_j)/etc_i
                            # if self.input.is_debug or self.input.is_debug_cycle_error:
                            #     print("i=", i.id, ", j=", j.id, ", etc_i=", etc_i, ", etc_j=", etc_i, ", error", error)
                            #     print("Error between nodes cycle time ", error, " between nodes ", i.id, " and ", j.id, "; cycles:", i.cycle)
                            if error > self.input.precision:
                                if self.iter_counter % 100000 == 0 and (self.input.is_debug or self.input.is_debug_cycle_error):
                                    print("Error between nodes cycle time ", error, " between nodes ", i.id, " and ",
                                          j.id, "; cycles:", i.cycle)

                                return False
                    return True
                else:
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

    def validate_run(self):
        has_transmiting_node = False
        transmitting_node = None

        for node in self.nodes:
            if has_transmiting_node and node.state == NodeState.TX_DATA:
                raise ValueError('Multiples transmitting nodes found:', node.id, ' and ', transmitting_node.id)
            if node.state == NodeState.TX_DATA:
                has_transmiting_node = True
                transmitting_node = node

    def serve_node_idle(self, node):
        """
            Check if node has RTS to transmit.
            If so, init transmission process
            Otherwise stay idle for some time
        """
        if node.event_time == self.time and node.state == NodeState.IDLE:

            temp = node.cycle_times

            s = 0.0
            sent_rts_count = 0
            has_idle = False
            finished_in_success = False
            finished_in_failure = False
            for e in node.cycle_times:
                if "idle" in e:
                    has_idle = True
                if "success" in e:
                    finished_in_success = True
                if "failure" in e:
                    finished_in_failure = True
                if "rts" in e:
                    sent_rts_count += 1
                if e.__contains__("out") or e.__contains__("backoff"):
                    if e.__contains__("out"):
                        s += e["out"]["end"] - e["out"]["start"]
                    else:
                        s += e["backoff"]["end"] - e["backoff"]["start"]
                else:
                    for v in e.values():
                        s+= v

            node.statistics.cycle_time2 +=s

            if not node.cycle_times:
                if self.input.is_debug or self.input.is_debug_cycle_error:
                    print("Note, cycle is empty:", node.cycle_times)
                    print("It is ok if this occurs at the start, otherwise this is strange")
            else:
                if len(node.cycle_times) == 1:
                    if has_idle:
                        node.statistics.trajectory_times["idle"] += s
                        node.statistics.trajectory_cycle_count["idle"] += 1
                    else:
                        raise ValueError('Found cycle time with length 1 and it is not idle loop. That is incorrect. Cycle:', node.cycle_times)
                else:
                    if not(finished_in_success or finished_in_failure):
                        print(finished_in_success)
                        print(finished_in_failure)
                        print(not(finished_in_success or finished_in_failure))
                        raise ValueError('Incorrect cycle. Cycle should contain success or failure state:', node.cycle_times)
                    if finished_in_success and finished_in_failure:
                        raise ValueError('Incorrect cycle. Cycle cannot contain success and failure state:', node.cycle_times)
                    if finished_in_failure:
                        node.statistics.trajectory_times["failure"] += s
                        node.statistics.trajectory_cycle_count["failure"] += 1
                    if finished_in_success:
                        node.statistics.trajectory_times["success with " + str(sent_rts_count) + " rts"] += s
                        node.statistics.trajectory_cycle_count["success with " + str(sent_rts_count) + " rts"] += 1


            node.cycle_times = []

            if self.input.is_debug or self.input.is_debug_cycle_info:
                print("Node", node.id, " cycle with duration", f'{s * pow(10, 9) :.4f}', "cleared! \nDeleted cycle:")
                for item in temp:
                    for key, value in item.items():
                        if key.__contains__("out"):
                            print("     ", key, ": start[", value["start"], "] end[", value["end"], "] = ", f'{(value["end"] - value["start"]) * pow(10, 9) :.4f}', "ns")
                        elif key.__contains__("backoff"):
                            print("     ", key, ": start[", value["start"], "] end[", value["end"], "] = ", f'{(value["end"] - value["start"]) * pow(10, 9) :.4f}', "ns")
                        else:
                            print("     ", key, ":", f'{value * pow(10, 9) :.4f}', "ns")
                print()

            if self.input.is_debug:
                print("     Node", node.id, ":", node.state.value, ", cycle ", node.cycle, ", attempt ", node.attempt)

            if node.cycle_start_time is None:
                node.cycle_start_time = self.time

            if random.random() < node.input.p_a:
                node.state = NodeState.BO
                node.cycle += 1
                node.attempt = 1
                node.event_time = self.time + self.generate_backoff_time(node)

                if self.input.is_debug:
                    print("     Node", node.id, " goes to BACKOFF until", node.event_time)
                node.cycle_times.append({"backoff": {"start": self.time, "end": node.event_time}})

                if self.input.is_debug:
                    print("Node", node.id, " cycle states: ", node.cycle_times)
            else:
                node.cycle += 1
                node.idle_cycle += 1

                node.state = NodeState.IDLE
                #  for discrete case: node.event_time = self.time + 1.0
                # node.event_time = self.time + 1.0
                node.event_time = self.time + self.input.tau_g_cts \
                                  + self.input.tau_g_data \
                                  + self.input.tau_g_ack

                if self.input.is_debug:
                    print("     Node", node.id, " keep staying IDLE")

                node.cycle_times.append({"idle" : node.event_time - self.time})
                if self.input.is_debug:
                    print("Node", node.id, " cycle states: ", node.cycle_times)

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

            node.cycle_times.append({"rts" : node.event_time - self.time})
            if self.input.is_debug:
                print("node", node.id, " cycle states: ", node.cycle_times)

    def serve_node_tx_rts(self, node):
        """
            Transmit RTS to gateway
        """
        if node.event_time == self.time and node.state == NodeState.TX_RTS:
            if self.input.is_debug:
                print("     Node", node.id, ":", node.state.value, ", cycle ", node.cycle, ", attempt ", node.attempt)

            node.statistics.rts_time += self.input.tau_g_rts

            node.state = NodeState.OUT
            node.event_time = self.time + self.input.tau_g_rts + self.input.tau_out
            # node.state = NodeState.BO
            # node.attempt += 1
            # node.event_time = self.time + self.generate_backoff_time(node)

            rts_msg = RTSMessage(node.id)
            rts_msg.id = str(node.id) + "_" + str(self.time)
            rts_msg.reached_gateway_at = self.time + self.input.tau_g_rts + node.get_propagation_time()
            rts_msg.transmission_time = self.input.tau_g_rts
            rts_msg.propagation_time = node.get_propagation_time()

            self.gateway.received_rts_messages[rts_msg.id] = rts_msg

            if self.input.is_debug:
                print("     Node", node.id, "sent RTS, RTS arrive to gateway at", rts_msg.reached_gateway_at)
                print("     Node", node.id, "goes to OUT until", node.event_time)

            node.cycle_times.append({"out" : {"start": self.time + self.input.tau_g_rts, "end": node.event_time}})
            if self.input.is_debug:
                print("node", node.id, " cycle states: ", node.cycle_times)

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
                node.event_time = self.time + self.generate_backoff_time(node)

                if self.input.is_debug:
                    print("     Node", node.id, " goes to BACKOFF #", node.attempt, "until", node.event_time)

                node.cycle_times.append({"backoff": {"start": self.time, "end": node.event_time}})
                if self.input.is_debug:
                    print("Node", node.id, " cycle states: ", node.cycle_times)
            else:
                if node.attempt == self.input.N_retry + 1:
                    node.state = NodeState.FAILURE
                    node.event_time = self.time

                    if self.input.is_debug:
                        print("     Node", node.id, " goes to FAILURE in ", node.attempt, "attempt")

                    node.cycle_times.append({"failure" : node.event_time - self.time })
                    if self.input.is_debug:
                        print("Node", node.id, " cycle states: ", node.cycle_times)
                else:
                    node.state = NodeState.BO
                    node.attempt += 1
                    node.event_time = self.time + self.generate_backoff_time(node)

                    if self.input.is_debug:
                        print("     Node", node.id, " goes to BACKOFF #", node.attempt, "until", node.event_time)

                    node.cycle_times.append(
                        {"backoff": {"start": self.time, "end": node.event_time}})
                    if self.input.is_debug:
                        print("Node", node.id, " cycle states: ", node.cycle_times)

    def serve_node_rx_cts(self, node):
        """
            If node receive CTS for other node, wait until end of transmission
            Else transmit data
        """
        if node.event_time == self.time and node.state == NodeState.RX_CTS:
            if self.input.is_debug:
                print("     Node", node.id, ":", node.state.value, ", cycle ", node.cycle, ", attempt ", node.attempt)


            if node.cts.node_id != node.id:
                for n, i in enumerate(reversed(node.cycle_times)):
                    if i.keys().__contains__("out") or i.keys().__contains__("backoff"):
                        if i.keys().__contains__("out"):
                            node.cycle_times[len(node.cycle_times) - n - 1]["out"]["end"] = self.time
                            break
                        elif i.keys().__contains__("backoff"):
                            node.cycle_times[len(node.cycle_times) - n - 1]["backoff"]["end"] = self.time
                            break

                node.state = NodeState.WAIT
                # for discrete case: self.time + 1.0
                # node.event_time = self.time + 1.0
                node.event_time = self.time \
                                  + self.input.tau_g_data \
                                  + self.input.tau_p_max \
                                  + self.input.tau_g_ack \
                                  + self.input.tau_p_max
                if self.input.is_debug:
                    print("     Node", node.id, " goes to WAIT because cts from ", node.cts.node_id, "until",
                          node.event_time)
                node.cts = None

                node.cycle_times.append({"wait"  : node.event_time - self.time})
                if self.input.is_debug:
                    print("Node", node.id, " cycle states: ", node.cycle_times)
            else:
                for n, i in enumerate(reversed(node.cycle_times)):
                    if i.keys().__contains__("out"):
                        node.cycle_times.remove(i)
                        break

                node.cts = None
                node.state = NodeState.TX_DATA
                # for discrete case: self.time + 1.0
                # node.event_time = self.time + 1.0
                node.event_time = self.time \
                                  + self.input.tau_g_data \
                                  + node.get_propagation_time() \
                                  + self.input.tau_g_ack \
                                  + node.get_propagation_time()

                self.gateway.state = GatewayState.RX_DATA
                # for discrete case: self.gateway.event_time = self.time + 1.0
                # self.gateway.event_time = self.time + 1.0
                self.gateway.event_time = self.time \
                                          + self.input.tau_g_data \
                                          + node.get_propagation_time() \
                                          + self.input.tau_g_ack

                if self.input.is_debug:
                    print("     Node", node.id, " goes to TX DATA until", node.event_time)
                    print("     Gateway goes to RX DATA until", self.gateway.event_time)

                node.cycle_times.append({"data tx" : node.event_time - self.time} )
                if self.input.is_debug:
                    print("Node", node.id, " cycle states: ", node.cycle_times)

    def serve_node_wait(self, node):
        if node.event_time == self.time and node.state == NodeState.WAIT:
            if self.input.is_debug:
                print("     Node", node.id, ":", node.state.value, ", cycle ", node.cycle, ", attempt ", node.attempt)

            node.state = NodeState.BO
            node.event_time = self.time + self.generate_backoff_time(node)

            if self.input.is_debug:
                print("     Node", node.id, " goes to BACKOFF #", node.attempt, "until", node.event_time)

            node.cycle_times.append({"backoff": {"start": self.time, "end": node.event_time}})
            if self.input.is_debug:
                print("Node", node.id, " cycle states: ", node.cycle_times)

    def serve_node_tx_data(self, node):
        if node.event_time == self.time and node.state == NodeState.TX_DATA:
            if self.input.is_debug:
                print("     Node", node.id, ":", node.state.value, ", cycle ", node.cycle, ", attempt ", node.attempt)

            node.statistics.data_time += self.input.tau_g_data
            data_tx_nodes_count = 0.0
            for n in self.nodes:
                if n.state == NodeState.TX_DATA:
                    data_tx_nodes_count += 1
            node.statistics.data_transmissions_count += 1
            node.statistics.parallel_transmitting_nodes += data_tx_nodes_count

            node.state = NodeState.SUCCESS
            node.event_time = self.time

            if self.input.is_debug:
                print("     Node", node.id, " goes to SUCCESS in ", node.attempt, "attempt")

            node.cycle_times.append({"success" : node.event_time - self.time })
            if self.input.is_debug:
                print("Node", node.id, " cycle states: ", node.cycle_times)

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

                # node.cycle_times.append({"idle" : node.event_time - self.time} )
                # print("Node", node.id, " cycle states: ", node.cycle_times)

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

                # node.cycle_times.append({"idle" : node.event_time - self.time})
                # print("Node", node.id, " cycle states: ", node.cycle_times)
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
                        if rts.id != other_rts.id and rts.reached_gateway_at >= (
                            other_rts.reached_gateway_at - other_rts.transmission_time):
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

                            if cts_message.reached_node_at <= node.event_time and node.state == NodeState.OUT \
                                    or (self.input.sensing == True and node.state == NodeState.BO):
                                # if message arrives during back off then serve it
                                node.state = NodeState.RX_CTS
                                node.event_time = cts_message.reached_node_at
                                node.cts = cts_message

                                if self.input.is_debug:
                                    print("     CTS sent to node", node.id, " and will reach it at",
                                          cts_message.reached_node_at)

                                node.cycle_times.append({"cts": node.event_time - self.time})
                                if self.input.is_debug:
                                    print("Node", node.id, " cycle states: ", node.cycle_times)
                            # otherwise let's consider such CTS as lost

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

    def generate_backoff_time(self, node):
        """
            For discrete case use: int(numpy.random.uniform(0, node.attempt * self.input.T_max))
            For time durations use: numpy.random.uniform(0, node.attempt * self.input.T_max)
        """
        bo = numpy.random.uniform(0, node.attempt * self.input.T_max)
        if self.input.is_debug:
            print("#generate_backoff_time: node :", node.id, ", attempt:", node.attempt, ", max value:", node.attempt * self.input.T_max, ", generated value:", bo)
        return bo

    def find_mean_node_statistic_values(self):
        for node in self.nodes:
            cycles_count = 1 if node.cycle == 0 else node.cycle
            idle_cycles_count = 1 if node.idle_cycle == 0 else node.idle_cycle
            node.statistics.total_cycle_count = node.cycle
            node.statistics.cycle_time = node.statistics.cycle_time / cycles_count
            node.statistics.cycle_time2 = node.statistics.cycle_time2 / cycles_count
            node.statistics.rts_time = node.statistics.rts_time / cycles_count
            node.statistics.data_time = node.statistics.data_time / cycles_count
            node.statistics.failure_count = node.statistics.failure_count / (cycles_count - idle_cycles_count)
            node.statistics.success_count = node.statistics.success_count / (cycles_count - idle_cycles_count)

            for key in node.statistics.trajectory_times.keys():
                if node.statistics.trajectory_cycle_count[key] == 0:
                    node.statistics.trajectory_times[key] = 0.0
                else:
                    node.statistics.trajectory_times[key] = node.statistics.trajectory_times[key] / node.statistics.trajectory_cycle_count[key]

    def find_gateway_statistic_values(self):
        self.gateway.statistics.received_rts += self.gateway.statistics.ignored_rts

        if self.gateway.statistics.received_rts == 0:
            self.gateway.statistics.blocking_probability_by_call = 0.0
        else:
            self.gateway.statistics.blocking_probability_by_call = (
                                                                   self.gateway.statistics.blocked_rts + self.gateway.statistics.ignored_rts) / self.gateway.statistics.received_rts

    def internal_debug(self):
        if self.input.is_debug and not self.input.auto_continue:
            print()
            user_input = input("[?] Press Enter in order to continue or input 'True' to enabled auto continue mode: ")
            if bool(user_input) == True:
                self.input.auto_continue = True

    def debug(self):

        total_cycle_count = 0.0
        failure_count = 0.0
        success_count = 0.0
        cycle_time = 0.0
        cycle_time2 = 0.0
        rts_time = 0.0
        data_time = 0.0
        parallel_data_tx = 0.0

        trajectory_times = {}
        trajectory_cycle_count = {}

        temp_total_cycle_count = 0.0
        temp_failure_count = 0.0
        temp_success_count = 0.0
        temp_cycle_time = 0.0
        temp_cycle_time2 = 0.0
        temp_rts_time = 0.0
        temp_data_time = 0.0
        temp_parallel_data_tx = 0.0
        temp_trajectory_times = {}
        temp_trajectory_cycle_count = {}

        for node in self.nodes:
            temp_total_cycle_count += node.statistics.total_cycle_count
            temp_failure_count += node.statistics.failure_count
            temp_success_count += node.statistics.success_count
            temp_cycle_time += node.statistics.cycle_time
            temp_cycle_time2 += node.statistics.cycle_time2
            temp_rts_time += node.statistics.rts_time
            temp_data_time += node.statistics.data_time

            if node.statistics.data_transmissions_count == 0:
                temp_parallel_data_tx += 0
            else:
                temp_parallel_data_tx += node.statistics.parallel_transmitting_nodes / node.statistics.data_transmissions_count

            for k,v in node.statistics.trajectory_times.items():
                if k not in temp_trajectory_times:
                    temp_trajectory_times[k] = 0.0
                temp_trajectory_times[k] += v

            for k,v in node.statistics.trajectory_cycle_count.items():
                if k not in temp_trajectory_cycle_count:
                    temp_trajectory_cycle_count[k] = 0.0
                temp_trajectory_cycle_count[k] += v

        total_cycle_count += temp_total_cycle_count / len(self.nodes)
        failure_count += temp_failure_count / len(self.nodes)
        success_count += temp_success_count / len(self.nodes)
        cycle_time += temp_cycle_time / len(self.nodes)
        cycle_time2 += temp_cycle_time2 / len(self.nodes)
        rts_time += temp_rts_time / len(self.nodes)
        data_time += temp_data_time / len(self.nodes)
        parallel_data_tx += temp_parallel_data_tx / len(self.nodes)

        for k in temp_trajectory_times.keys():
            trajectory_times[k] = temp_trajectory_times[k] / len(self.nodes)

        for k in temp_trajectory_cycle_count.keys():
            trajectory_cycle_count[k] = temp_trajectory_cycle_count[k] / len(self.nodes)

        if cycle_time == 0:
            tau = None
            tau_data = None
        else:
            tau = rts_time / cycle_time
            tau_data = data_time / cycle_time

        if cycle_time2 == 0:
            tau2 = 0.0
            tau_data2 = 0.0
        else :
            tau2 = rts_time / cycle_time2
            tau_data2 = data_time / cycle_time2

        print("Summary:")
        print("     pa:", self.input.p_a)
        print("     avg node cycles:", total_cycle_count)
        print("     parallel data transmissions number: ", parallel_data_tx)
        print("     - probabilities -")
        print("         p{failure}:", failure_count)
        print("         p{success}", success_count)
        print("     - times -")
        print("         rts time: " + f'{rts_time * pow(10, 9) :.4f}' + " ns")
        print("         rts data_time: " + f'{data_time * pow(10, 9) :.4f}' + " ns")
        print("         cycle time: " + f'{cycle_time * pow(10, 9) :.4f}' + " ns")
        print("         cycle time2: " + f'{cycle_time2 * pow(10, 9) :.4f}' + " ns")
        print("     - tau -")
        print("         tau:", tau)
        print("         tau2:", tau2)
        print("         tau_data:", tau_data if tau_data is not None else None)
        print("         tau_data2:", tau_data2)
        print("     - tau relation -")
        print("         tau/tau_data:", tau/tau_data if tau is not None else None)

        print("         tau2/tau_data2:", tau2/tau_data2 if tau_data2 is not None and tau_data2!=0 else None)
        print("     - tau relation check -")
        print("         t_rts/(t_packet*(1-p)):", self.input.tau_g_rts/(self.input.tau_g_data*(1-failure_count)))

        print("     - Trajectory times -")
        for k, v in trajectory_times.items():
            print("     ",k, ": ",  f'{v * pow(10, 9) :.4f}' + " ns", " (", trajectory_cycle_count[k] ,"cycles)")

        print("")

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
            print("     rts time: " + f'{node.statistics.rts_time * pow(10, 9) :.4f}' + " ns")
            print("     cycle time: " + f'{node.statistics.cycle_time * pow(10, 9) :.4f}' + " ns")
            print("     cycle time: " + f'{node.statistics.cycle_time2 * pow(10, 9) :.4f}' + " ns")
            if node.statistics.data_transmissions_count == 0:
                print("     parallel data transmissions count:", 0)
            else:
                print("     parallel data transmissions count:", node.statistics.parallel_transmitting_nodes / node.statistics.data_transmissions_count)
            print("     trajectory times:")
            for k, v in node.statistics.trajectory_times.items():
                print("     ", k, ": ",  f'{v * pow(10, 9) :.4f}' + " ns", " (", node.statistics.trajectory_cycle_count[k], "cycles)")
