import random

import numpy

from unibo_rudn.core.gateway import Gateway, GatewayState
from unibo_rudn.core.message import RTSMessage, CTSMessage
from unibo_rudn.core.node import Node, NodeState
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
        for i in range(1, self.input.NN + 1):
            self.nodes.append(Node(i, self.input.sphere_radius, self.input))

    def run(self):
        """
        Run simulation
        """

        if self.input.is_debug:
            print("\n# Simulation started\n")

        while not self.is_simulation_finished():
            if self.input.is_debug:
                print("Time =", pow(10,9)* self.time)

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
            if self.input.Nretx is None:
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
                # for node in self.nodes:
                #     if node.statistics.probability_of_success < self.input.planned_success:
                #         return False
                # return True
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
        if self.input.is_debug:
            for node in self.nodes:
                print("   Node", node.id, ", next event at", pow(10,9)*node.event_time)

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
            print()
            print("New time: ", pow(10,9) * event_time, ", event:", next_state)

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
                if "backoff" in e:
                    node.bo_state +=1
                    node.statistics.not_tx_rx_time += e["backoff"]["end"] - e["backoff"]["start"]
                    node.statistics.total_not_tx_rx_time += e["backoff"]["end"] - e["backoff"]["start"]
                if "success" in e:
                    finished_in_success = True
                    node.success_state +=1
                if "failure" in e:
                    finished_in_failure = True
                    node.failure_state +=1
                if "idle" in e:
                    has_idle = True
                    node.idle_state +=1
                    node.statistics.idle_time += self.input.Tidle
                    node.statistics.total_idle_time += self.input.Tidle

                    node.statistics.not_tx_rx_time += self.input.Tidle
                    node.statistics.total_not_tx_rx_time += self.input.Tidle
                if "rts" in e:
                    sent_rts_count += 1
                    node.rts_state +=1
                    node.statistics.rts_time += self.input.Trts
                    node.statistics.total_rts_time += self.input.Trts
                if "cts" in e:
                    node.cts_state +=1
                if "out" in e:
                    node.out_state +=1

                    node.statistics.not_tx_rx_time += e["out"]["end"] - e["out"]["start"]
                    node.statistics.total_not_tx_rx_time += e["out"]["end"] - e["out"]["start"]
                if "wait" in e:
                    node.wait_state +=1
                    node.statistics.wait_time += self.input.Twait
                    node.statistics.total_wait_time += self.input.Twait

                    node.statistics.not_tx_rx_time += e["wait"]["end"] - e["wait"]["start"]
                    node.statistics.total_not_tx_rx_time += e["wait"]["end"] - e["wait"]["start"]
                if "data" in e:
                    node.data_state +=1
                    node.statistics.data_time += self.input.Tdata
                    node.statistics.channel_busy_time += self.input.Tcts + self.input.Tdata + self.input.Tack
                    node.statistics.total_data_time += self.input.Tdata
                for k, v in e.items():
                    s += e[k]["end"] - e[k]["start"]

            node.statistics.cycle_time2 +=s

            if not node.cycle_times:
                if self.input.is_debug or self.input.is_debug_cycle_error:
                    print("Note, cycle is empty:", node.cycle_times)
                    print("It is ok if this occurs at the start, otherwise this is strange")
                    print()
            else:
                if len(node.cycle_times) == 1:
                    if has_idle:
                        node.statistics.trajectory_times["idle"] += s
                        node.statistics.trajectory_cycle_count["idle"] += 1
                        node.cycle += 1
                        node.idle_cycle += 1
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
                    """node.cycle += 1"""
                    if finished_in_failure:
                        node.statistics.trajectory_times["failure"] += s
                        node.statistics.trajectory_cycle_count["failure"] += 1
                        node.statistics.total_failure_cycle_time += s

                    if finished_in_success:
                        node.statistics.trajectory_times["success with " + str(sent_rts_count) + " rts"] += s
                        node.statistics.trajectory_cycle_count["success with " + str(sent_rts_count) + " rts"] += 1
                        node.statistics.total_success_cycle_time += s



            node.cycle_times = []

            if self.input.is_debug or self.input.is_debug_cycle_info:
                print("Node", node.id, " finished cycle with duration", f'{s * pow(10, 9) :.4f}', "! \nCycle stacktrace:")

                if not temp:
                    print("     > cycle is empty")

                for item in temp:
                    for key, value in item.items():
                        print("     ", key, ": start[", pow(10,9) * value["start"], "] end[", pow(10,9) * value["end"], "] = ",
                              f'{(value["end"] - value["start"]) * pow(10, 9) :.4f}', "ns")
                print()

            if self.input.is_debug:
                print("     Node", node.id, ":", node.state.value, ", cycle ", node.cycle, ", attempt ", node.attempt, ", | GW state: ", self.gateway.state)

            if node.cycle_start_time is None:
                node.cycle_start_time = self.time

            if random.random() < node.input.p_a:
                node.state = NodeState.BO
                node.attempt = 1
                node.event_time = self.time + self.generate_backoff_time(node)

                if self.input.is_debug:
                    print("     Node", node.id, " goes to BACKOFF until", pow(10,9) * node.event_time)
                node.cycle_times.append({"backoff": {"start": self.time, "end": node.event_time}})

                if self.input.is_debug:
                    print("             Node", node.id, " cycle states: ")
                    self.debug_node_cycle_times(node)
            else:
                node.state = NodeState.IDLE
                #  for discrete case: node.event_time = self.time + 1.0
                # node.event_time = self.time + 1.0
                node.event_time = self.time + self.input.Tcts \
                                  + self.input.Tdata \
                                  + self.input.Tack

                node.statistics.cycle_time += node.event_time - self.time
                node.cycle_start_time = None
                node.cycle_end_time = None

                if self.input.is_debug:
                    print("     Node", node.id, " keep staying IDLE")

                node.cycle_times.append({"idle": {"start": self.time, "end": node.event_time}})
                if self.input.is_debug:
                    print("             Node", node.id, " cycle states: ")
                    self.debug_node_cycle_times(node)

    def serve_node_backoff(self, node):
        """
            After waiting back off window go to RTS transmission
        """
        if node.event_time == self.time and node.state == NodeState.BO:
            if self.input.is_debug:
                print("     Node", node.id, ":", node.state.value, ", cycle ", node.cycle, ", attempt ", node.attempt, ", | GW state: ", self.gateway.state)

            node.state = NodeState.TX_RTS
            node.event_time = self.time + self.input.Trts

            rts_msg = RTSMessage(node.id)
            rts_msg.id = str(node.id) + "_" + str(self.time)
            rts_msg.reached_gateway_at = self.time + self.input.Trts + node.get_propagation_time()
            rts_msg.transmission_time = self.input.Trts
            rts_msg.propagation_time = node.get_propagation_time()

            self.gateway.received_rts_messages[rts_msg.id] = rts_msg
            self.gateway.statistics.received_rts += 1

            if self.input.is_debug:
                print("     Node", node.id, " goes to TX RTS until", pow(10,9) * node.event_time)
                print("     Node", node.id, "sent RTS, RTS arrive to gateway at", pow(10,9) * rts_msg.reached_gateway_at)

            node.cycle_times.append({"rts": {"start": self.time, "end": node.event_time}})
            if self.input.is_debug:
                print("             Node", node.id, " cycle states: ")
                self.debug_node_cycle_times(node)

    def serve_node_tx_rts(self, node):
        """
            Transmit RTS to gateway
        """
        if node.event_time == self.time and node.state == NodeState.TX_RTS:
            if self.input.is_debug:
                print("     Node", node.id, ":", node.state.value, ", cycle ", node.cycle, ", attempt ", node.attempt, ", | GW state: ", self.gateway.state)

            node.state = NodeState.OUT
            node.event_time = self.time + self.input.Tout


            if self.input.is_debug:
                print("     Node", node.id, "goes to OUT until", pow(10,9) * node.event_time)

            node.cycle_times.append({"out": {"start": self.time, "end": node.event_time}})
            if self.input.is_debug:
                print("             Node", node.id, " cycle states: ")
                self.debug_node_cycle_times(node)

    def serve_node_out(self, node):
        """
            No CTS were received.
            Go to the next attempt if attempts limit wasn't reached
            Go to failure state if attempt limit was reached
        """
        if node.event_time == self.time and node.state == NodeState.OUT:
            if self.input.is_debug:
                print("     Node", node.id, ":", node.state.value, ", cycle ", node.cycle, ", attempt ", node.attempt, ", | GW state: ", self.gateway.state)

            if self.input.Nretx is None:
                node.state = NodeState.BO
                node.attempt += 1
                node.event_time = self.time + self.generate_backoff_time(node)

                if self.input.is_debug:
                    print("     Node", node.id, " goes to BACKOFF #", node.attempt, "until", pow(10,9) * node.event_time)

                node.cycle_times.append({"backoff": {"start": self.time, "end": node.event_time}})
                if self.input.is_debug:
                    print("             Node", node.id, " cycle states: ")
                    self.debug_node_cycle_times(node)
            else:
                if node.attempt == self.input.Nretx + 1:
                    node.state = NodeState.FAILURE
                    node.event_time = self.time

                    if self.input.is_debug:
                        print("     Node", node.id, " goes to FAILURE in ", node.attempt, "attempt")

                    node.cycle_times.append({"failure": {"start": self.time, "end": node.event_time}})
                    if self.input.is_debug:
                        print("             Node", node.id, " cycle states: ")
                        self.debug_node_cycle_times(node)
                else:
                    node.state = NodeState.BO
                    node.attempt += 1
                    node.event_time = self.time + self.generate_backoff_time(node)

                    if self.input.is_debug:
                        print("     Node", node.id, " goes to BACKOFF #", node.attempt, "until", pow(10,9) * node.event_time)

                    node.cycle_times.append(
                        {"backoff": {"start": self.time, "end": node.event_time}})
                    if self.input.is_debug:
                        print("             Node", node.id, " cycle states: ")
                        self.debug_node_cycle_times(node)

    def serve_node_rx_cts(self, node):
        """
            If node receive CTS for other node, wait until end of transmission
            Else transmit data
        """
        if node.event_time == self.time and node.state == NodeState.RX_CTS:
            if self.input.is_debug:
                print("     Node", node.id, ":", node.state.value, ", cycle ", node.cycle, ", attempt ", node.attempt, ", | GW state: ", self.gateway.state)


            if node.cts.node_id != node.id:
                for n, i in enumerate(reversed(node.cycle_times)):
                    if i.keys().__contains__("out") or i.keys().__contains__("backoff"):
                        if i.keys().__contains__("out"):
                            node.cycle_times[len(node.cycle_times) - n - 1]["out"]["end"] = node.cts.reached_node_at - node.cts.transmission_time
                            break
                        elif i.keys().__contains__("backoff"):
                            node.cycle_times[len(node.cycle_times) - n - 1]["backoff"]["end"] = node.cts.reached_node_at - node.cts.transmission_time
                            break

                node.state = NodeState.WAIT
                # for discrete case: self.time + 1.0
                # node.event_time = self.time + 1.0
                node.event_time = self.time + self.input.Twait

                if self.input.is_debug:
                    print("     Node", node.id, " goes to WAIT because cts from ", node.cts.node_id, "until",
                          pow(10,9) * node.event_time)
                node.cts = None

                node.cycle_times.append({"wait": {"start": self.time, "end": node.event_time}})
                if self.input.is_debug:
                    print("             Node", node.id, " cycle states: ")
                    self.debug_node_cycle_times(node)
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
                                  + self.input.Tdata \
                                  + node.get_propagation_time() \
                                  + self.input.Tack \
                                  + node.get_propagation_time()

                self.gateway.state = GatewayState.RX_DATA
                # for discrete case: self.gateway.event_time = self.time + 1.0
                # self.gateway.event_time = self.time + 1.0
                self.gateway.event_time = self.time \
                                          + self.input.Tdata \
                                          + node.get_propagation_time() \
                                          + self.input.Tack

                if self.input.is_debug:
                    print("     Node", node.id, " goes to TX DATA until", pow(10,9) * node.event_time)
                    print("     Gateway goes to RX DATA until", pow(10,9) * self.gateway.event_time)

                node.cycle_times.append({"data": {"start": self.time, "end": node.event_time}})
                if self.input.is_debug:
                    print("             Node", node.id, " cycle states: ")
                    self.debug_node_cycle_times(node)

    def serve_node_wait(self, node):
        if node.event_time == self.time and node.state == NodeState.WAIT:
            if self.input.is_debug:
                print("     Node", node.id, ":", node.state.value, ", cycle ", node.cycle, ", attempt ", node.attempt, ", | GW state: ", self.gateway.state)

            node.statistics.probability_of_wait += 1
            node.state = NodeState.BO
            node.event_time = self.time + self.generate_backoff_time(node)

            if self.input.is_debug:
                print("     Node", node.id, " goes to BACKOFF #", node.attempt, "until", pow(10,9) * node.event_time)

            node.cycle_times.append({"backoff": {"start": self.time, "end": node.event_time}})
            if self.input.is_debug:
                print("             Node", node.id, " cycle states: ")
                self.debug_node_cycle_times(node)

    def serve_node_tx_data(self, node):
        if node.event_time == self.time and node.state == NodeState.TX_DATA:
            if self.input.is_debug:
                print("     Node", node.id, ":", node.state.value, ", cycle ", node.cycle, ", attempt ", node.attempt, ", | GW state: ", self.gateway.state)

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

            node.cycle_times.append({"success": {"start": self.time, "end": node.event_time}})
            if self.input.is_debug:
                print("             Node", node.id, " cycle states: ")
                self.debug_node_cycle_times(node)

    def serve_node_failure(self, node):
        """
            Terminate node activity for Absorbing mode
            Go to the next cycle for Cyclic mode
        """
        if node.event_time == self.time and node.state == NodeState.FAILURE:
            if self.input.is_debug:
                print("     Node", node.id, ":", node.state.value, ", cycle ", node.cycle, ", attempt ", node.attempt, ", | GW state: ", self.gateway.state)

            node.cycle_end_time = self.time

            node.statistics.probability_of_failure += 1
            node.statistics.cycle_time += node.cycle_end_time - node.cycle_start_time
            node.cycle += 1

            node.cycle_start_time = None
            node.cycle_end_time = None

            if self.input.mode == SimulationType.ABSORBING:
                node.state = NodeState.FAILURE
                node.event_time = None
            if self.input.mode == SimulationType.CYCLIC:
                node.state = NodeState.IDLE
                node.event_time = self.time

            if self.input.mode not in list(map(lambda c: c, SimulationType)):
                raise ValueError("Unsupported simulation mode:", self.input.mode)

    def serve_node_success(self, node):
        """
            Terminate node activity for Absorbing mode
            Go to the next cycle for Cyclic mode
        """
        if node.event_time == self.time and node.state == NodeState.SUCCESS:
            if self.input.is_debug:
                print("     Node", node.id, ":", node.state.value, ", cycle ", node.cycle, ", attempt ", node.attempt, ", | GW state: ", self.gateway.state)

            node.cycle_end_time = self.time

            node.statistics.probability_of_success += 1
            node.statistics.cycle_time += node.cycle_end_time - node.cycle_start_time
            node.cycle += 1

            node.cycle_start_time = None
            node.cycle_end_time = None

            if self.input.mode == SimulationType.ABSORBING:
                node.state = NodeState.SUCCESS
                node.event_time = None
            if self.input.mode == SimulationType.CYCLIC:
                node.state = NodeState.IDLE
                node.event_time = self.time

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
                print("     Gateway", self.gateway.state, ", event time:", pow(10,9) * self.gateway.event_time if self.gateway.event_time is not None else self.gateway.event_time)

            already_received_rts = []

            for id, rts in self.gateway.received_rts_messages.items():
                if rts.reached_gateway_at == self.time:
                    if self.input.is_debug:
                        print("     RTS from Node", rts.node_id, "reached gateway at", pow(10,9) * rts.reached_gateway_at)

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

                            self.gateway.statistics.blocked_rts += 1
                            already_received_rts.append(col.id)

                        if self.input.is_debug:
                            print("     There is a collision between", collision_rts_ids)
                    else:
                        # no collision, send CTS
                        if self.input.is_debug:
                            print("     There were no collisions")


                        self.gateway.statistics.not_blocked_rts += 1

                        for node in self.nodes:
                            # if node sensing is off, send CTS only to target node
                            if not self.input.sensing:
                                if rts.node_id != node.id:
                                    continue

                            cts_message = CTSMessage(rts.node_id)
                            cts_message.id = str(node.id) + "_" + str(self.time)
                            cts_message.reached_node_at = self.time + self.input.Tcts + node.get_propagation_time()
                            cts_message.transmission_time = self.input.Tcts
                            cts_message.propagation_time = node.get_propagation_time()

                            if cts_message.reached_node_at <= node.event_time \
                                    and node.state == NodeState.OUT \
                                    or (self.input.sensing == True and node.state == NodeState.BO):
                                # if message arrives during back off then serve it
                                node.state = NodeState.RX_CTS
                                node.event_time = self.time + self.input.Tcts + node.get_propagation_time()
                                node.cts = cts_message

                                if self.input.is_debug:
                                    print("     CTS sent to node", node.id, " and will reach it at",
                                          pow(10,9) * cts_message.reached_node_at)

                                node.cycle_times.append({"cts": {"start": self.time, "end": node.event_time}})
                                if self.input.is_debug:
                                    print("             Node", node.id, " cycle states: ")
                                    self.debug_node_cycle_times(node)
                            # otherwise let's consider such CTS as lost

            # remove served rts
            for rts_id in already_received_rts:
                self.gateway.received_rts_messages.pop(rts_id, None)

    def serve_gateway_rx_data(self):
        if self.gateway.state == GatewayState.RX_DATA and self.time == self.gateway.event_time:
            if self.input.is_debug:
                print("     Gateway", self.gateway.state, ", event time:", pow(10,9) * self.gateway.event_time)

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
            For discrete case use: int(numpy.random.uniform(0, node.attempt * self.input.Tbo))
            For time durations use: numpy.random.uniform(0, node.attempt * self.input.Tbo)
        """
        bo = numpy.random.uniform(0, node.attempt * self.input.Tmax *self.input.Tbo)
        # if self.input.is_debug:
        #     print("#generate_backoff_time: node :", node.id, ", attempt:", node.attempt, ", max value:", pow(10,9) * node.attempt * self.input.Tbo, ", generated value:", pow(10,9) * bo)
        return bo

    def find_mean_node_statistic_values(self):
        for node in self.nodes:
            cycles_count = node.cycle
            idle_cycles_count = node.idle_cycle
            node.statistics.total_cycle_count = node.cycle
            node.statistics.total_idle_cycle_count = node.idle_cycle
            node.statistics.cycle_time = node.statistics.cycle_time / cycles_count
            node.statistics.cycle_time2 = node.statistics.cycle_time2 / cycles_count
            node.statistics.idle_time = node.statistics.idle_time / cycles_count
            node.statistics.not_tx_rx_time = node.statistics.not_tx_rx_time / cycles_count
            node.statistics.rts_time = node.statistics.rts_time / cycles_count
            node.statistics.data_time = node.statistics.data_time / cycles_count
            node.statistics.wait_time = node.statistics.wait_time / cycles_count
            node.statistics.channel_busy_time = node.statistics.channel_busy_time / cycles_count
            node.statistics.probability_of_failure = node.statistics.probability_of_failure / (cycles_count - (0 if idle_cycles_count == 0 else idle_cycles_count)) if (cycles_count - (0 if idle_cycles_count == 0 else idle_cycles_count)) != 0 else 1
            node.statistics.probability_of_success = node.statistics.probability_of_success / (cycles_count - (0 if idle_cycles_count == 0 else idle_cycles_count)) if (cycles_count - (0 if idle_cycles_count == 0 else idle_cycles_count)) != 0 else 1
            node.statistics.probability_of_wait = node.statistics.probability_of_wait / (cycles_count - (0 if idle_cycles_count == 0 else idle_cycles_count)) if (cycles_count - (0 if idle_cycles_count == 0 else idle_cycles_count)) != 0 else 1
            node.statistics.probability_of_wait = node.statistics.probability_of_wait * self.input.Twait / node.statistics.cycle_time2

            for key in node.statistics.trajectory_times.keys():
                if node.statistics.trajectory_cycle_count[key] == 0:
                    node.statistics.trajectory_times[key] = 0.0
                else:
                    node.statistics.trajectory_times[key] = node.statistics.trajectory_times[key] / node.statistics.trajectory_cycle_count[key]

    def find_gateway_statistic_values(self):
        self.gateway.statistics.received_rts += self.gateway.statistics.ignored_rts

        if self.gateway.statistics.received_rts == 0:
            self.gateway.statistics.probability_of_collision = 0.0
        else:
            # before we counted here also self.gateway.statistics.ignored_rts
            self.gateway.statistics.probability_of_collision = (
                                                                   self.gateway.statistics.blocked_rts ) / self.gateway.statistics.received_rts

    def internal_debug(self):
        if self.input.is_debug and not self.input.auto_continue:
            print()
            user_input = input("[?] Press Enter in order to continue or input 'True' to enabled auto continue mode: \n")
            if bool(user_input) == True:
                self.input.auto_continue = True

    def debug_node_cycle_times(self, node):
        for time in node.cycle_times:
            string = ""
            for state, times in time.items():
                string += state + ": "
                for k, v in times.items():
                    string += str(k) + " = " + str(pow(10, 9) * v) + " ns, "
            string = string[:-2]
            print("                 ", string)

    def debug(self):

        total_cycle_count = 0.0
        total_idle_cycle_count = 0.0
        failure_count = 0.0
        success_count = 0.0
        wait_count = 0.0

        cycle_time = 0.0
        cycle_time2 = 0.0
        cycle_time3 = 0.0
        idle_time = 0.0
        not_tx_rx_time = 0.0
        rts_time = 0.0
        data_time = 0.0
        wait_time = 0.0
        channel_busy_time = 0.0
        parallel_data_tx = 0.0

        trajectory_times = {}
        trajectory_cycle_count = {}

        temp_total_cycle_count = 0.0
        temp_total_idle_cycle_count = 0.0
        temp_failure_count = 0.0
        temp_success_count = 0.0
        temp_wait_count = 0.0
        temp_cycle_time = 0.0
        temp_cycle_time2 = 0.0
        temp_cycle_time3 = 0.0
        temp_idle_time = 0.0
        temp_not_tx_rx_time = 0.0
        temp_rts_time = 0.0
        temp_data_time = 0.0
        temp_wait_time = 0.0
        temp_channel_busy_time = 0.0
        temp_parallel_data_tx = 0.0
        temp_trajectory_times = {}
        temp_trajectory_cycle_count = {}

        mean_idle_cycles = 0
        mean_bo_cycles = 0
        mean_rts_cycles = 0
        mean_out_cycles = 0
        mean_cts_cycles = 0
        mean_wait_cycles = 0
        mean_data_cycles = 0
        mean_success_cycles = 0
        mean_failure_cycles = 0

        total_idle_time = 0.0
        total_not_tx_rx_time = 0.0
        total_success_time = 0.0
        total_failure_time = 0.0
        total_rts_time = 0.0
        total_data_time = 0.0
        total_wait_time = 0.0

        for node in self.nodes:
            temp_total_cycle_count += node.statistics.total_cycle_count
            temp_total_idle_cycle_count += node.statistics.total_idle_cycle_count
            temp_failure_count += node.statistics.probability_of_failure
            temp_success_count += node.statistics.probability_of_success
            temp_wait_count += node.statistics.probability_of_wait
            temp_cycle_time += node.statistics.cycle_time
            temp_cycle_time2 += node.statistics.cycle_time2
            temp_cycle_time3 += node.statistics.cycle_time2 * node.cycle
            temp_idle_time += node.statistics.idle_time
            temp_not_tx_rx_time += node.statistics.not_tx_rx_time
            temp_rts_time += node.statistics.rts_time
            temp_data_time += node.statistics.data_time
            temp_wait_time += node.statistics.wait_time
            temp_channel_busy_time += node.statistics.channel_busy_time

            total_idle_time += node.statistics.total_idle_time
            total_not_tx_rx_time += node.statistics.total_not_tx_rx_time
            total_success_time += node.statistics.total_success_cycle_time
            total_failure_time += node.statistics.total_failure_cycle_time
            total_rts_time += node.statistics.total_rts_time
            total_data_time += node.statistics.total_data_time
            total_wait_time += node.statistics.total_wait_time

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

            mean_idle_cycles += node.idle_cycle
            mean_bo_cycles += node.bo_state
            mean_rts_cycles += node.rts_state
            mean_out_cycles += node.out_state
            mean_cts_cycles += node.cts_state
            mean_wait_cycles += node.wait_state
            mean_data_cycles += node.data_state
            mean_success_cycles += node.success_state
            mean_failure_cycles += node.failure_state

        total_cycle_count += temp_total_cycle_count / len(self.nodes)
        total_idle_cycle_count += temp_total_idle_cycle_count / len(self.nodes)
        failure_count += temp_failure_count / len(self.nodes)
        success_count += temp_success_count / len(self.nodes)
        wait_count += temp_wait_count / len(self.nodes)
        cycle_time += temp_cycle_time / len(self.nodes)
        cycle_time2 += temp_cycle_time2 / len(self.nodes)
        cycle_time3 += temp_cycle_time3 / len(self.nodes)
        idle_time += temp_idle_time / len(self.nodes)
        not_tx_rx_time += temp_not_tx_rx_time / len(self.nodes)
        rts_time += temp_rts_time / len(self.nodes)
        data_time += temp_data_time / len(self.nodes)
        wait_time += temp_wait_time / len(self.nodes)
        channel_busy_time += temp_channel_busy_time / len(self.nodes)
        parallel_data_tx += temp_parallel_data_tx / len(self.nodes)

        mean_idle_cycles /= len(self.nodes)
        mean_bo_cycles /= len(self.nodes)
        mean_rts_cycles /= len(self.nodes)
        mean_out_cycles /= len(self.nodes)
        mean_cts_cycles /= len(self.nodes)
        mean_wait_cycles /= len(self.nodes)
        mean_data_cycles /= len(self.nodes)
        mean_success_cycles /= len(self.nodes)
        mean_failure_cycles /= len(self.nodes)

        total_idle_time /= len(self.nodes)
        total_not_tx_rx_time /= len(self.nodes)
        total_success_time /= len(self.nodes)
        total_failure_time /= len(self.nodes)
        total_rts_time /= len(self.nodes)
        total_data_time /= len(self.nodes)
        total_wait_time /= len(self.nodes)

        for k in temp_trajectory_times.keys():
            trajectory_times[k] = temp_trajectory_times[k] / len(self.nodes)

        for k in temp_trajectory_cycle_count.keys():
            trajectory_cycle_count[k] = temp_trajectory_cycle_count[k] / len(self.nodes)

        if cycle_time == 0:
            tau = None
            tau_data = None
            tau_channel_busy = None
        else:
            tau = rts_time / cycle_time
            tau_data = data_time / cycle_time
            tau_channel_busy = channel_busy_time / cycle_time

        if cycle_time2 == 0:
            tau2 = 0.0
            tau_data2 = 0.0
            tau_channel_busy2 = 0.0
        else:
            tau2 = rts_time / cycle_time2
            tau_data2 = data_time / cycle_time2
            tau_channel_busy2 = channel_busy_time / cycle_time2

        print("Summary:")
        print("     node count:", self.input.NN)
        print("     pa:", self.input.p_a)
        print("     avg node cycles:", total_cycle_count)
        print("     avg node idle cycles:", total_idle_cycle_count)
        print("     avg node w/o idle cycles:", total_cycle_count-total_idle_cycle_count)
        print("     parallel data transmissions number: ", parallel_data_tx - 1)
        print("     - probabilities -")
        print("             p{failure}:", failure_count)
        print("             p{success}", success_count)
        print("             ---")
        print("             p{data}", self.input.Tdata * success_count / cycle_time2)
        print("             p{wait}", wait_count)
        print("     - times -")
        print("             idle time: " + f'{idle_time * pow(10, 9) :.4f}' + " ns")
        print("             time w/o tx/rx: " + f'{not_tx_rx_time * pow(10, 9) :.4f}' + " ns")
        print("             rts time: " + f'{rts_time * pow(10, 9) :.4f}' + " ns")
        print("             data_time: " + f'{data_time * pow(10, 9) :.4f}' + " ns")
        print("             wait_time: " + f'{wait_time * pow(10, 9) :.4f}' + " ns")
        print("             cycle time: " + f'{cycle_time * pow(10, 9) :.4f}' + " ns")
        print("             cycle time2: " + f'{cycle_time2 * pow(10, 9) :.4f}' + " ns")
        print("             cycle time3: " + f'{(cycle_time3 / total_cycle_count) * pow(10, 9) :.4f}' + " ns")
        print("             mean_idle_cycles * Tidle / avg_cycles_count = " + f'{mean_idle_cycles * self.input.Tidle / total_cycle_count * pow(10, 9) :.4f}' + " ns")
        print("             mean_rts_cycles * tau_rts / avg_cycles_count = " + f'{mean_rts_cycles * self.input.Trts / total_cycle_count * pow(10, 9) :.4f}' + " ns")
        print("             mean_data_cycles * tau_data / avg_cycles_count = " + f'{mean_data_cycles * self.input.Tdata / total_cycle_count * pow(10, 9) :.4f}' + " ns")
        print("             mean_wait_cycles * Twait / avg_cycles_count = " + f'{mean_wait_cycles * self.input.Twait / total_cycle_count * pow(10, 9) :.4f}' + " ns")
        print("     - Total times -")
        print("             total simulation time: " + f'{self.time * pow(10, 9) :.4f}' + " ns")
        print("             total idle time: " + f'{total_idle_time * pow(10, 9) :.4f}' + " ns")
        print("             total time w/o tx/rx: " + f'{total_not_tx_rx_time * pow(10, 9) :.4f}' + " ns")
        print("             total rts time / total time: " + f'{(total_rts_time / self.time)  :.4f}')
        print("             total data time: " + f'{total_data_time * pow(10, 9) :.4f}' + " ns")
        print("             total data time / total time: " + f'{(total_data_time / self.time)  :.4f}' )
        print("             total wait time: " + f'{total_wait_time * pow(10, 9) :.4f}' + " ns")
        print("             total wait time / total time: " + f'{(total_wait_time / self.time)  :.4f}' )
        print("             total success time: " + f'{total_success_time * pow(10, 9) :.4f}' + " ns")
        print("             total success time / total time: " + f'{(total_success_time / self.time)  :.4f}')
        print("             total failure time: " + f'{total_failure_time * pow(10, 9) :.4f}' + " ns")
        print("             total failure time / total time: " + f'{total_failure_time / self.time  :.4f}')
        print("     - Trajectory times -")
        for k, v in trajectory_times.items():
            print("         ",k, ": ",  f'{v * pow(10, 9) :.4f}' + " ns", " (", trajectory_cycle_count[k] ,"cycles)")
        print("     - State visits - ")
        print("             total state visits: ", sum([mean_idle_cycles, mean_bo_cycles, mean_rts_cycles, mean_out_cycles, mean_cts_cycles, mean_wait_cycles, mean_data_cycles, mean_success_cycles,  mean_failure_cycles]))
        print("             mean_idle_cycles =",mean_idle_cycles)
        print("             mean_bo_cycles =",mean_bo_cycles)
        print("             mean_rts_cycles =",mean_rts_cycles)
        print("             mean_out_cycles =",mean_out_cycles)
        print("             mean_cts_cycles =",mean_cts_cycles)
        print("             mean_wait_cycles =",mean_wait_cycles)
        print("             mean_data_cycles =",mean_data_cycles)
        print("             mean_success_cycles =",mean_success_cycles)
        print("             mean_failure_cycles =",mean_failure_cycles)
        print("     - Times validation - ")
        print("             mean_rts_cycles * tau_rts = " + f'{mean_rts_cycles * self.input.Trts * pow(10, 9) :.4f}' + " ns")
        print("             mean rts time * avg. cycles count = " + f'{total_cycle_count * rts_time * pow(10, 9) :.4f}' + " ns")
        print("             -")
        print("             mean_data_cycles * tau_data = " + f'{mean_data_cycles * self.input.Tdata * pow(10, 9) :.4f}' + " ns")
        print("             mean data time * avg. cycles count =" + f'{total_cycle_count * data_time * pow(10, 9) :.4f}' + " ns")
        print("             -")
        print("             mean_rts_cycles * tau_rts / mean_rts_cycles = " + f'{mean_rts_cycles * self.input.Trts / mean_rts_cycles * pow(10, 9) :.4f}' + " ns")
        print("             mean rts time * avg. cycles count / mean_rts_cyces = " + f'{total_cycle_count * rts_time / mean_rts_cycles * pow(10, 9) :.4f}' + " ns")
        print("             -")
        print("             mean_data_cycles * tau_data / mean_rts_cycles = " + f'{mean_data_cycles * self.input.Tdata / mean_data_cycles * pow(10, 9) :.4f}' + " ns")
        print("             mean data time * avg. cycles count / mean_data_cycles =" + f'{total_cycle_count * data_time / mean_data_cycles * pow(10, 9) :.4f}' + " ns")
        print("             -")
        print("     - tau -")
        print("             tau:", tau)
        print("             tau2:", tau2)
        print("             tau_data:", tau_data if tau_data is not None else None)
        print("             tau_data2:", tau_data2)
        print("             tau_data3:", (self.input.Tdata * mean_success_cycles) / self.time)
        print("             tau_channel_busy:", tau_channel_busy)
        print("             tau_channel_busy2:", tau_channel_busy2 if tau_channel_busy2 is not None else None)
        print("     - tau relation -")
        print("             tau/tau_data:", tau/tau_data if tau is not None and tau_data != 0 else None)
        print("             tau2/tau_data2:", tau2/tau_data2 if tau_data2 is not None and tau_data2!=0 else None)
        print("     - tau relation check -")
        print("             t_rts/(t_packet*(1-p)):", self.input.Trts/(self.input.Tdata*(1-pow(failure_count, (1/(self.input.Nretx+1)))))) if (self.input.Tdata*(1-pow(failure_count, (1/(self.input.Nretx+1))))) != 0 else None


        print("")

        print("Gateway:")
        print("     received rts:", self.gateway.statistics.received_rts)
        print("     blocked rts:", self.gateway.statistics.blocked_rts)
        print("     not blocked rts:", self.gateway.statistics.not_blocked_rts)
        print("     ignored rts:", self.gateway.statistics.ignored_rts)
        print("     Blocking probability by call:", self.gateway.statistics.probability_of_collision)
        print("")
        for node in self.nodes:
            print("Node", node.id, ":", node.state.value)
            print("     total cycles:", node.statistics.total_cycle_count)
            print("     idle cycles:", node.statistics.total_idle_cycle_count)
            print("     - Probabilities - ")
            print("         success:", node.statistics.probability_of_success)
            print("         failure:", node.statistics.probability_of_failure)
            print("         wait:", node.statistics.probability_of_wait)
            print("     - Average times -")
            print("         idle time: " + f'{node.statistics.idle_time * pow(10, 9) :.4f}' + " ns")
            print("         time w/o tx/rx: " + f'{node.statistics.not_tx_rx_time * pow(10, 9) :.4f}' + " ns")
            print("         rts time: " + f'{node.statistics.rts_time * pow(10, 9) :.4f}' + " ns")
            print("         data time: " + f'{node.statistics.data_time * pow(10, 9) :.4f}' + " ns")
            print("         wait time: " + f'{node.statistics.wait_time * pow(10, 9) :.4f}' + " ns")
            print("         channel busy time: " + f'{node.statistics.channel_busy_time * pow(10, 9) :.4f}' + " ns")
            print("         cycle time: " + f'{node.statistics.cycle_time * pow(10, 9) :.4f}' + " ns")
            print("         cycle time2: " + f'{node.statistics.cycle_time2 * pow(10, 9) :.4f}' + " ns")
            print("     - Total times - ")
            print("         total simulation time:" + f'{self.time * pow(10, 9) :.4f}' + " ns")
            print("         total idle time:" + f'{node.statistics.total_idle_time * pow(10, 9) :.4f}' + " ns")
            print("         total time w/o tx/rx:" + f'{node.statistics.total_not_tx_rx_time * pow(10, 9) :.4f}' + " ns")
            print("         total rts time:" + f'{node.statistics.total_rts_time * pow(10, 9) :.4f}' + " ns")
            print("         total total rts time / total simulation time:" + f'{( node.statistics.total_rts_time / self.time) :.4f}' )
            print("         total data time:" + f'{node.statistics.total_data_time * pow(10, 9) :.4f}' + " ns")
            print("         total data time / total simulation time:" + f'{( node.statistics.total_data_time / self.time) :.4f}' )
            print("         total wait time:" + f'{node.statistics.total_wait_time * pow(10, 9) :.4f}' + " ns")
            print("         total wait time / total simulation time:" + f'{( node.statistics.total_wait_time / self.time) :.4f}' )
            print("         total success cycle time:" + f'{node.statistics.total_success_cycle_time * pow(10, 9) :.4f}' + " ns")
            print("         total success cycle time / total simulation time:" + f'{( node.statistics.total_success_cycle_time / self.time) :.4f}' )
            print("         total failure cycle time:" + f'{node.statistics.total_failure_cycle_time * pow(10, 9) :.4f}' + " ns")
            print("         total failure cycle time / total simulation time:" + f'{( node.statistics.total_failure_cycle_time / self.time) :.4f}' )
            if node.statistics.data_transmissions_count == 0:
                print("     parallel data transmissions count:", 0)
            else:
                print("     parallel data transmissions count:", node.statistics.parallel_transmitting_nodes / node.statistics.data_transmissions_count - 1)
            print("     trajectory times:")
            for k, v in node.statistics.trajectory_times.items():
                print("         ", k, ": ",  f'{v * pow(10, 9) :.4f}' + " ns", " (", node.statistics.trajectory_cycle_count[k], "cycles)")
            print("      - states visits - ")
            print("         idle:", node.idle_state)
            print("         bo:", node.bo_state)
            print("         rts:", node.rts_state)
            print("         out:", node.out_state)
            print("         wait:", node.wait_state)
            print("         cts:", node.cts_state)
            print("         data:", node.data_state)
            print("         success:", node.success_state)
            print("         failure:", node.failure_state)
