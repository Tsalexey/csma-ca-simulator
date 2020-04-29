from unibo_rudn.core.Messages import BeaconMessage, RTSMessage, ACKMessage, CTSMessage
from unibo_rudn.core.gateway import Gateway
from unibo_rudn.core.node import Node


class Simulation:
    def __init__(self, input):
        """
        Create a simulation according to provided input
        """
        self.validate_input(input)

        # simulation input data
        self.input = input

        # simulation parameters
        self.time = 0

        # statistics
        self.collision_duration = 0.0
        self.collision_calls = 0

        self.collision_time_blocking_probability = 0.0
        self.collision_call_blocking_probability = 0.0
        self.collision_call_blocking_probability_on_gw = 0.0

        self.nodes_count_that_transmitted_data = 0

        # gateway
        self.gateway = Gateway(self.input.tau_g_beacon, self.input.tau_g_cts, self.input.tau_g_ack,
                               self.input.tau_channel_busy, self.input.is_debug)

        # nodes
        self.nodes = []
        for i in range(1, self.input.nodes_number + 1):
            self.nodes.append(
                Node(i, self.input.sphere_radius, self.input.T_max, self.input.tau_g_rts, self.input.tau_out,
                     self.input.is_debug))

    def validate_input(self, input):
        """
        Validate if input has all the necessary fields
        Throws an exception in case of invalid input
        """
        if input.is_debug is None:
            input.is_debug = True
        if input.auto_continue is None:
            input.auto_continue = True

        exception_message = ""
        is_valid = True

        if input.nodes_number is None:
            is_valid = False
            exception_message += "You should provide number of nodes (nodes_number variable)!\n"

        if input.sphere_radius is None or input.sphere_radius < 0:
            is_valid = False
            exception_message += "You should provide valid sphere radius more then 0 (sphere_radius variable)!\n"

        if input.N_retry is not None and input.N_retry < 0:
            is_valid = False
            exception_message += "You should provide valid RTS retry limit (N_retry variable)!\n"

        if input.tau_g_rts is not None and input.tau_g_rts < 0:
            is_valid = False
            exception_message += "You should provide valid transmission time for RTS message (tau_g_rts variable)!\n"

        if input.tau_g_cts is not None and input.tau_g_cts < 0:
            is_valid = False
            exception_message += "You should provide valid transmission time for CTS message (tau_g_cts variable)!\n"

        if input.tau_g_ack is not None and input.tau_g_ack < 0:
            is_valid = False
            exception_message += "You should provide valid transmission time for ACK message (tau_g_ack variable)!\n"

        if input.tau_g_data is not None and input.tau_g_data < 0:
            is_valid = False
            exception_message += "You should provide valid transmission time for data message (tau_g_data variable)!\n"

        if input.T_max is not None and input.T_max < 0:
            is_valid = False
            exception_message += "You should provide valid delay before sending RTS (T_max variable)!\n"

        if input.tau_p_max is not None and input.tau_p_max < 0:
            is_valid = False
            exception_message += "You should provide valid maximal propagation time (tau_p_max variable)!\n"

        if input.tau_out is not None and input.tau_out < 0:
            is_valid = False
            exception_message += "You should provide valid window contention time (tau_out variable)!\n"

        if input.tau_channel_busy is not None and input.tau_channel_busy < 0:
            is_valid = False
            exception_message += "You should provide validdata transmission time (tau_channel_busy variable)!\n"

        if not is_valid:
            raise ValueError(exception_message)

    def run(self):
        """
        Run simulation
        """

        if self.input.is_debug:
            print("\n# Simulation started\n")

        while not self.is_simulation_finished():
            if self.input.is_debug:
                print("[*] Time", self.time)
                self.debug_run()
                self.debug_next_event_times(5)

            # it is time to send beacon message
            if self.time == 0.0:
                if self.input.is_debug:
                    print("It is time to generate Beacon at gateway")
                beacon_message = BeaconMessage("Gateway", self.time, self.input.tau_g_beacon)
                for node in self.nodes:
                    node.beacon_message = beacon_message
                    node.beacon_message.node_arrival_time = node.beacon_message.generated_at + node.beacon_message.transmission_time + node.get_propagation_time()
                    node.next_rts_generation_time = node.beacon_message.node_arrival_time
                    if self.input.is_debug:
                        print("     Node", node.id, "will receive beacon at", node.beacon_message.node_arrival_time)
            else:
                for node in self.nodes:
                    # if node did't receive ack message
                    if not node.ack_message:

                        if (self.input.N_retry is None or self.input.N_retry + 1 >= node.transmission_attempt) \
                                and node.next_rts_generation_time is not None and self.time == node.next_rts_generation_time:
                            if self.input.is_debug: print("It is time to generate RTS for Node", node.id)
                            rts_message = RTSMessage(node.id, self.time)
                            rts_message.sent_from_node_at = self.time + node.get_tau_w(node.transmission_attempt,
                                                                                       node.T_max)
                            rts_message.arrived_to_gateway_at = rts_message.sent_from_node_at + node.get_propagation_time() + node.tau_g_rts
                            rts_message.propagation_time = node.get_propagation_time()
                            rts_message.transmission_time = node.tau_g_rts
                            rts_message.attempt_number = node.transmission_attempt

                            node.transmitted_rts_messages.append(rts_message)
                            node.next_rts_generation_time = rts_message.sent_from_node_at + node.tau_out
                            node.transmission_attempt += 1

                            self.gateway.rts_messages_to_be_processed.append(rts_message)
                            self.gateway.received_rts_count += 1
                            if self.input.is_debug:
                                print("Node", node.id, "has generated RTS at", self.time, ", RTS will be sent at",
                                      rts_message.sent_from_node_at, ", RTS will arrive to Gateway at",
                                      rts_message.arrived_to_gateway_at)

                        # it is time to receive cts from gateway
                        if node.cts_message is not None and self.time == node.cts_message.arrived_at:
                            if self.input.is_debug:
                                print("It is time to process CTS for Node", node.cts_message.id, "by Node", node.id)

                            node.next_rts_generation_time = self.time \
                                                            + node.cts_message.transmission_time \
                                                            + node.cts_message.propagation_time \
                                                            + self.input.tau_g_data \
                                                            + node.cts_message.propagation_time \
                                                            + self.input.tau_g_ack \
                                                            + node.cts_message.propagation_time

                            node.received_cts_messages.append(node.cts_message)

                            if node.cts_message.id == node.id:
                                self.gateway.send_ack_at = self.time \
                                                           + node.get_propagation_time() \
                                                           + self.input.tau_g_data \
                                                           + node.get_propagation_time() \
                                                           + self.input.tau_g_ack

                                self.gateway.send_ack_to = node.id
                                node.next_rts_generation_time = None
                            node.cts_message = None

                # time to send ack from gateway and receive ack by node
                if self.gateway.send_ack_at is not None and self.gateway.send_ack_at == self.time:
                    if self.input.is_debug:
                        print("It is time to send ACK from Gateway to Node", self.gateway.send_ack_to)
                    for node in self.nodes:
                        if node.id == self.gateway.send_ack_to:
                            node.ack_message = ACKMessage(node.id, self.time, self.input.tau_g_ack, node.get_propagation_time())
                            node.finished_at = self.time + node.ack_message.transmission_time + node.ack_message.propagation_time
                            self.gateway.rts_messages_to_be_processed = list(
                                filter(lambda v: v.id != node.id, self.gateway.rts_messages_to_be_processed))
                    self.gateway.send_ack_at = None
                    self.gateway.send_ack_to = None

                # time to process rts by gateway and send cts to node
                for rts in self.gateway.rts_messages_to_be_processed:
                    if self.time == rts.arrived_to_gateway_at:
                        if self.input.is_debug: print("It is time to process RTS at Gateway from Node", rts.id)

                        self.gateway.total_working_time += self.input.tau_g_rts

                        collision_rts_list = []

                        collision_start_time = rts.arrived_to_gateway_at - rts.propagation_time
                        collision_end_time = rts.arrived_to_gateway_at

                        for other_rts in self.gateway.rts_messages_to_be_processed:
                            if rts.rts_id != other_rts.rts_id and rts.arrived_to_gateway_at >= (
                                        other_rts.arrived_to_gateway_at - other_rts.transmission_time):
                                collision_rts_list.append(other_rts)
                                if collision_end_time < other_rts.arrived_to_gateway_at:
                                    collision_end_time = other_rts.arrived_to_gateway_at

                        # we got a collision
                        if collision_rts_list:
                            collision_rts_list.append(rts)
                            self.collision_duration += self.input.tau_g_rts
                            self.collision_calls += len(collision_rts_list)
                            self.gateway.blocked_time += self.input.tau_g_rts

                            collision_ids = []
                            collision_rts_ids = []
                            for msg in collision_rts_list:
                                collision_ids.append(msg.id)
                                collision_rts_ids.append(msg.rts_id)

                            if self.input.is_debug:
                                print("There is a collision between RTS from node", rts.id, "and", collision_ids)

                            self.gateway.unsuccessful_processed_rts_messages.append(collision_rts_list)
                            self.gateway.rts_messages_to_be_processed = list(
                                filter(lambda v: v.rts_id not in collision_rts_ids,
                                       self.gateway.rts_messages_to_be_processed))
                        # we got no collisions
                        else:
                            self.gateway.rts_messages_to_be_processed.remove(rts)
                            self.gateway.successful_processed_rts_messages.append(rts)

                            cts_message = CTSMessage("Gateway", self.time, self.input.tau_g_cts)
                            cts_message.id = rts.id
                            cts_message.rts_attempt_number = rts.attempt_number

                            if self.input.is_debug:
                                print("CTS is sent by gateway at", self.time)
                            for node in self.nodes:
                                node.cts_message = cts_message
                                node.cts_message.propagation_time = node.get_propagation_time()
                                node.cts_message.arrived_at = node.cts_message.generated_at + node.cts_message.propagation_time + node.cts_message.transmission_time
                                if self.input.is_debug:
                                    print("Node", node.id, "will receive CTS at", (
                                        node.cts_message.generated_at + node.cts_message.transmission_time + node.cts_message.propagation_time))

            # find next event and update system time
            self.update_time()

        self.calculate_statistics()

        if self.input.is_debug:
            print("\n# Simulation ended at", self.time)
            self.debug_run()

    def calculate_statistics(self):
        temp_transmitted_rts_count = 0
        temp_nodes_count_that_transmitted_data = 0
        temp_D_total = 0.0
        temp_finished_at_count = 0

        for node in self.nodes:
            temp_transmitted_rts_count += len(node.transmitted_rts_messages)
            if node.finished_at is not None:

                temp_finished_at_count += 1
            if node.ack_message is not None:
                temp_D_total += node.ack_message.arrived_at
                temp_nodes_count_that_transmitted_data += 1

        self.nodes_count_that_transmitted_data = temp_nodes_count_that_transmitted_data
        self.transmitted_rts_count = temp_transmitted_rts_count / len(self.nodes)

        # D total
        if self.nodes_count_that_transmitted_data == 0:
            self.D_total = 0
        else:
            self.D_total = temp_D_total / self.nodes_count_that_transmitted_data

        # tau_data / D_total
        if self.D_total == 0:
            self.tau_data_divided_by_D_total = 0
        else:
            self.tau_data_divided_by_D_total = (self.nodes_count_that_transmitted_data / self.input.nodes_number) * self.input.tau_g_data / self.D_total

        # 1 - tau_data / D_total
        if self.D_total == 0:
            self.one_minus_tau_data_divided_by_D_total = 1
        else:
            self.one_minus_tau_data_divided_by_D_total = 1.0 - self.tau_data_divided_by_D_total

        temp_transmitted_rts_messages = 0
        temp_retransmitted_rts_messages = 0
        for node in self.nodes:
            temp_transmitted_rts_messages += len(node.transmitted_rts_messages)
            temp_retransmitted_rts_messages += (len(node.transmitted_rts_messages) - 1)

        self.transmitted_rts_messages = temp_transmitted_rts_messages / len(self.nodes)
        self.retransmitted_rts_messages = temp_retransmitted_rts_messages / len(self.nodes)

        # collision probability by time
        if self.time == 0:
            self.collision_time_blocking_probability = 0
        else:
            self.collision_time_blocking_probability = self.gateway.blocked_time / self.gateway.total_working_time

        # collision probability by call on gw
        processed_at_gw_count = len(self.gateway.unsuccessful_processed_rts_messages) + len(self.gateway.successful_processed_rts_messages)
        if processed_at_gw_count == 0:
            self.collision_call_blocking_probability = 0
        else:
            self.collision_call_blocking_probability = len(self.gateway.unsuccessful_processed_rts_messages) / processed_at_gw_count

        # D(n)
        self.D_n = {}
        D_counter = {}
        for node in self.nodes:
            if node.ack_message is not None and node.cts_message is not None:
                if node.cts_message.rts_attempt_number in self.D_n:
                    self.D_n[node.cts_message.rts_attempt_number] += node.finished_at
                    D_counter[node.cts_message.rts_attempt_number] += 1
                else:
                    self.D_n[node.cts_message.rts_attempt_number] = node.finished_at
                    D_counter[node.cts_message.rts_attempt_number] = 1
        for key, value in self.D_n.items():
            self.D_n[key] = self.D_n[key] / D_counter[key]


    def is_simulation_finished(self):
        """
        Check if it is time to stop simulation.
        Simulation will be stopped:
            1) if input has no RTS retry limit - when all the nodes transmit user data
            2) if input has RTS retry limit - when all the nodes exceed RTS retry limit or send user data
        """

        if self.input.is_debug:
            print("Check if gateway has no more rts to process =", self.gateway_has_no_more_rts_to_process())
            if self.input.N_retry is None:
                print("Check if RTS is transmitted by all the nodes =", self.is_rts_transmitted_by_all_nodes())
            else:
                print("Check if all the Nodes exceeded retry limit =", self.is_all_nodes_exceeded_retry_limit())

        if self.input.N_retry is None:
            return self.gateway_has_no_more_rts_to_process() and self.is_rts_transmitted_by_all_nodes()
        else:
            return self.gateway_has_no_more_rts_to_process() and self.is_all_nodes_exceeded_retry_limit()

    def gateway_has_no_more_rts_to_process(self):
        """
        Check if there are RTS which gateway should handle
        """

        return len(self.gateway.rts_messages_to_be_processed) == 0

    def is_rts_transmitted_by_all_nodes(self):
        """
        Check if all the nodes transmitted user data (in case of no retry limits)
        """

        for node in self.nodes:
            if node.ack_message is None and self.input.N_retry is None:
                return False
        return True

    def is_all_nodes_exceeded_retry_limit(self):
        """
        Check if all the nodes transmitted user data (in case of retry limits)
        """

        for node in self.nodes:
            if node.ack_message is None and (self.input.N_retry is not None and self.input.N_retry + 1 >= node.transmission_attempt):
                return False
        return True

    def update_time(self):
        """
        Find next event time
        """
        t1 = self.get_first_rts_transmission_time()
        t2 = self.get_first_cts_arrived_to_node_time()
        t3 = self.get_first_rts_arrived_to_gw_time()
        t4 = self.get_ack_time()

        times = []
        if t1 is not None: times.append(t1)
        if t2 is not None: times.append(t2)
        if t3 is not None: times.append(t3)
        if t4 is not None: times.append(t4)

        if not times:
            if self.input.is_debug:
                print("Seems all the Nodes have transmitted data or exceeded retry limit")
                print("Simulation should be finished")
        else:
            t = min(times)

            if self.input.is_debug:
                if t1 is not None and t == t1: event = "RTS transmission processing"
                if t2 is not None and t == t2: event = "CTS arrive processing"
                if t3 is not None and t == t3: event = "RTS arrive processing"
                if t4 is not None and t == t4: event = "ACK processing"
                print("Next event is", event, "at", t)
                print("----------")
            self.time = t

    def get_ack_time(self):
        time = None
        if self.gateway.send_ack_at is not None:
            time = self.gateway.send_ack_at
        return time

    def get_first_rts_transmission_time(self):
        """
        Find the time for the next RTS transmission
        """

        time = None
        for node in self.nodes:
            if node.ack_message is not None:
                continue
            if self.input.N_retry is not None and self.input.N_retry + 1 < node.transmission_attempt:
                continue
            if node.next_rts_generation_time is not None:
                if time is None or time > node.next_rts_generation_time:
                    time = node.next_rts_generation_time
        return time

    def get_first_cts_arrived_to_node_time(self):
        """
        Find the time for the next arriving CTS
        """

        time = None
        for node in self.nodes:
            if node.ack_message is not None:
                continue
            if self.input.N_retry is not None and self.input.N_retry + 1 < node.transmission_attempt:
                continue
            if node.cts_message is not None:
                if time is None or time > node.cts_message.arrived_at:
                    time = node.cts_message.arrived_at
        return time

    def get_first_rts_arrived_to_gw_time(self):
        """
        Find the time for next arriving RTS
        """

        time = None
        for rts in self.gateway.rts_messages_to_be_processed:
            if rts.arrived_to_gateway_at is not None and time is None:
                time = rts.arrived_to_gateway_at
            if time > rts.arrived_to_gateway_at:
                time = rts.arrived_to_gateway_at
        return time

    def debug_run(self):
        """
        Print debug information
        """

        if self.input.is_debug:
            print("[*] System state is:")
            print("     Gateway: rts to handle =", len(self.gateway.rts_messages_to_be_processed),
                  ", rts success=", len(self.gateway.successful_processed_rts_messages),
                  ", rts failure =", len(self.gateway.unsuccessful_processed_rts_messages),
                  ", collision time=", self.collision_duration,
                  ", collision prob = ", self.collision_time_blocking_probability)
            for node in self.nodes:
                print("     Node", node.id, ": data sent =", node.ack_message is not None, ",sent rts =",
                      len(node.transmitted_rts_messages), ", received cts =", len(node.received_cts_messages),
                      ", transmission attempt =", node.transmission_attempt, ", retry limit =", self.input.N_retry)
        if self.input.is_debug and not self.input.auto_continue:
            print()
            user_input = input("[?] Press Enter in order to continue or input 'True' to enabled auto continue mode: ")
            if bool(user_input) == True:
                self.input.auto_continue = True

    def debug_next_event_times(self, events_count):
        """
        Print info about next firts events
        """

        if self.input.is_debug:
            rts_generation_map = {}
            rts_sending_map = {}
            cts_receiving_map = {}
            for node in self.nodes:
                if node.next_rts_generation_time is not None:
                    rts_generation_map[node.next_rts_generation_time] = "Node " + str(
                        node.id) + " will generate new RTS at " + str(node.next_rts_generation_time)
                if node.cts_message is not None:
                    cts_receiving_map[node.cts_message.arrived_at] = "Node " + str(node.id) + " will process CTS at " + str(
                        node.cts_message.arrived_at)

            rts_arrived_at_gateway_map = {}
            rts_processed_at_gateway_map = {}
            for rts in self.gateway.rts_messages_to_be_processed:
                rts_arrived_at_gateway_map[rts.arrived_to_gateway_at] = "RTS from Node " + str(
                    rts.id) + " will arrive to gateway at " + str(rts.arrived_to_gateway_at)
                rts_processed_at_gateway_map[rts.processed_at_gateway_at] = "RTS from Node " + str(
                    rts.id) + " processing  will be finished at " + str(rts.processed_at_gateway_at)

            if rts_generation_map:
                print("     RTS generating:")
                for elem in sorted(rts_generation_map.items()):
                    print("         ", elem[1])
            if rts_sending_map:
                print("     RTS sending:")
                for elem in sorted(rts_sending_map.items()):
                    print("         ", elem[1])
            if cts_receiving_map:
                print("     CTS receiving:")
                for elem in sorted(cts_receiving_map.items()):
                    print("         ", elem[1])
            if rts_arrived_at_gateway_map:
                print("     RTS arriving:")
                for elem in sorted(rts_arrived_at_gateway_map.items())[:events_count]:
                    print("         ", elem[1])
            if rts_processed_at_gateway_map:
                print("     RTS processing:")
                for elem in sorted(rts_processed_at_gateway_map.items())[:events_count]:
                    print("         ", elem[1])
            print()
