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
                print("[*] Time =", self.time)
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
                self.gateway.start_serving_time = self.input.tau_g_beacon
            else:
                for node in self.nodes:
                    # if node did't receive ack message
                    if not node.ack_message:

                        # time to generate rts
                        if node.is_active \
                                and node.next_rts_generation_time is not None \
                                and self.time == node.next_rts_generation_time:
                            if self.input.is_debug:
                                print("It is time to generate RTS for Node", node.id)

                            rts_message = RTSMessage(node.id, self.time)
                            rts_message.sent_from_node_at = self.time + node.get_tau_w(node.transmission_attempt,
                                                                                       node.T_max)
                            rts_message.arrived_to_gateway_at = rts_message.sent_from_node_at + node.get_propagation_time() + node.tau_g_rts
                            rts_message.propagation_time = node.get_propagation_time()
                            rts_message.transmission_time = node.tau_g_rts

                            node.ready_to_transmit_rts[rts_message.rts_id] = rts_message
                            node.next_rts_generation_time = None
                            node.waiting_for_other_data_transmission_finished = None

                            if self.input.is_debug:
                                print("Node", node.id, "has generated RTS at", self.time, ", RTS will be sent at",
                                      rts_message.sent_from_node_at, ", RTS will arrive to Gateway at",
                                      rts_message.arrived_to_gateway_at)

                        # time to transmit rts
                        delete_rts_id_from_ready_to_transmit = []
                        for key, rts in node.ready_to_transmit_rts.items():
                            if rts.sent_from_node_at == self.time:
                                if self.input.is_debug:
                                    print("It is time to transmit RTS for Node", rts.id)

                                delete_rts_id_from_ready_to_transmit.append(rts.rts_id)

                                rts.attempt_number = node.transmission_attempt

                                node.transmitted_rts_messages[rts.rts_id]= rts
                                node.next_rts_generation_time = rts.sent_from_node_at + node.tau_out

                                node.transmission_attempt += 1

                                self.gateway.rts_messages_to_be_processed[rts.rts_id] = rts
                                self.gateway.received_rts_count += 1

                                if self.input.is_debug:
                                    print("Node", node.id, "has transmitted RTS at", self.time,
                                          ", RTS will arrive to Gateway at", rts.arrived_to_gateway_at)

                                if self.input.N_retry is not None and self.input.N_retry + 1 == node.transmission_attempt - 1:
                                    node.is_active = False

                        for msg in delete_rts_id_from_ready_to_transmit:
                            node.ready_to_transmit_rts.pop(msg, None)

                        # it is time to receive cts from gateway
                        if node.cts_message is not None and self.time == node.cts_message.arrived_at:
                            if self.input.is_debug:
                                print("It is time to process CTS for Node", node.cts_message.id
                                      , "by Node", node.id, ", CTS arrived at ", node.cts_message.arrived_at)
                            node.waiting_for_other_data_transmission_finished = True

                            node.ready_to_transmit_rts = {}

                            node.next_rts_generation_time = self.time \
                                                            + node.cts_message.transmission_time \
                                                            + self.input.tau_p_max \
                                                            + self.input.tau_g_data \
                                                            + self.input.tau_p_max \
                                                            + self.input.tau_g_ack \
                                                            + self.input.tau_p_max

                            node.received_cts_messages[node.cts_message.id] = node.cts_message

                            if node.cts_message.id == node.id:
                                node.stat_success.append(cts_message.rts_attempt_number)
                                node.next_rts_generation_time = None
                                node.waiting_for_other_data_transmission_finished = None

                                self.gateway.send_ack_at = self.time \
                                                           + node.get_propagation_time() \
                                                           + self.input.tau_g_data
                                                           # + node.get_propagation_time() \
                                                           # + self.input.tau_g_ack
                                self.gateway.send_ack_to = node.id

                                if self.input.is_debug:
                                    print("It is time to send ACK from Gateway to Node", self.gateway.send_ack_to)

                                node.ack_message = ACKMessage(node.id, self.gateway.send_ack_at, self.input.tau_g_ack,
                                                                      node.get_propagation_time())
                                node.finished_at = self.gateway.send_ack_at + node.ack_message.transmission_time + node.ack_message.propagation_time

                                self.gateway.start_serving_time = self.gateway.send_ack_at

                                self.gateway.send_ack_at = None
                                self.gateway.send_ack_to = None

                                self.gateway.last_ack_time = self.time

                            node.cts_message = None

                # time to process rts by gateway and send cts to node
                delete_rts_ids_from_gateway_rts_messages_to_be_processed = []

                for key, rts in self.gateway.rts_messages_to_be_processed.items():
                    if self.time == rts.arrived_to_gateway_at:
                        self.gateway.total_processed_rts_messages[rts.rts_id] = rts
                        self.gateway.total_working_time += self.input.tau_g_rts

                        delete_rts_ids_from_gateway_rts_messages_to_be_processed.append(rts.rts_id)

                        if self.input.is_debug:
                            print("It is time to process RTS at Gateway from Node", rts.id, " with id ", rts.rts_id)

                        collision_rts_list = []
                        collision_rts_ids = []
                        collision_ids = []

                        collision_start_time = rts.arrived_to_gateway_at - rts.propagation_time
                        collision_end_time = rts.arrived_to_gateway_at

                        for other_key, other_rts in self.gateway.rts_messages_to_be_processed.items():
                            if rts.rts_id != other_rts.rts_id and rts.arrived_to_gateway_at >= (
                                            other_rts.arrived_to_gateway_at - other_rts.transmission_time):
                                if other_rts.rts_id not in delete_rts_ids_from_gateway_rts_messages_to_be_processed \
                                            and other_rts.rts_id not in collision_rts_ids:
                                    collision_rts_list.append(other_rts)
                                    collision_rts_ids.append(other_rts.rts_id)
                                    collision_ids.append(other_rts.id)
                                    self.gateway.total_processed_rts_messages[other_rts.rts_id] = other_rts
                                    if self.input.is_debug:
                                        print("Collision with: node=", other_rts.id, ", rts id=", other_rts.rts_id,
                                              ", timing=",
                                              other_rts.arrived_to_gateway_at)
                                    if collision_end_time < other_rts.arrived_to_gateway_at:
                                        collision_end_time = other_rts.arrived_to_gateway_at

                        # we got a collision
                        if collision_rts_list:
                            collision_rts_list.append(rts)
                            collision_rts_ids.append(rts.rts_id)

                            self.gateway.blocked_time += self.input.tau_g_rts
                            self.gateway.number_of_collisions += 1
                            if self.input.is_debug:
                                print("There is a collision between RTS from node", rts.id, "and", collision_ids)
                                print("RTS message ids ", collision_rts_ids)

                            for col in collision_rts_list:
                                for node in self.nodes:
                                    if node.id == col.id:
                                        node.stat_collision.append(col.attempt_number)

                                delete_rts_ids_from_gateway_rts_messages_to_be_processed.append(col.rts_id)
                                self.gateway.unsuccessful_processed_rts_messages[col.rts_id] = col

                        # we got no collisions
                        else:
                            # for node in self.nodes:
                            #     if node.id == rts.id:
                            #         node.stat_success.append(rts.attempt_number)
                            self.gateway.end_serving_time = self.time
                            self.gateway.busy_time += self.gateway.end_serving_time - self.gateway.start_serving_time

                            self.gateway.successful_processed_rts_messages[rts.rts_id] = rts
                            self.gateway.cts_transmitted_to[rts.id] = True

                            if self.input.is_debug:
                                print("CTS is sent by gateway at", self.time, ", node.cts_message=", node.cts_message)

                            # temp = False
                            for node in self.nodes:
                                if node.cts_message is None:
                                    node.next_rts_generation_time = None

                                    cts_message = CTSMessage("Gateway", self.time, self.input.tau_g_cts)
                                    cts_message.id = rts.id
                                    cts_message.rts_attempt_number = rts.attempt_number
                                    node.cts_message = cts_message
                                    node.cts_message.propagation_time = node.get_propagation_time()
                                    cts_arrived_at = node.cts_message.generated_at + node.cts_message.transmission_time + node.cts_message.propagation_time
                                    node.cts_message.arrived_at = cts_arrived_at
                                    if self.input.is_debug:
                                        print("Node", node.id, "will receive CTS at", node.cts_message.arrived_at)
                            # if temp:
                            #     print("found hidden block:", rts.id)
                            #     self.gateway.stat_hidden_block.append(rts.id)

                for rts_id in delete_rts_ids_from_gateway_rts_messages_to_be_processed:
                    self.gateway.rts_messages_to_be_processed.pop(rts_id, None)

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
        if self.gateway.total_working_time == 0:
            self.collision_time_blocking_probability = 0
        else:
            self.collision_time_blocking_probability = self.gateway.blocked_time / self.gateway.total_working_time

        # collision probability by call on gw
        if len(self.gateway.total_processed_rts_messages) != 0:
            self.collision_call_blocking_probability = len(self.gateway.unsuccessful_processed_rts_messages) / len(self.gateway.total_processed_rts_messages)
        else:
            self.collision_call_blocking_probability = 0

        # collision probability by time (YG)
        if self.gateway.last_ack_time is not None:
            self.collision_gw_time_blocking_probability = self.gateway.total_working_time / self.gateway.last_ack_time
        else:
            self.collision_gw_time_blocking_probability = 0

        # D(n)
        self.D_n = {}
        self.D_n_counter = {}
        for node in self.nodes:
            if node.ack_message is not None and node.cts_message is not None:
                if node.cts_message.rts_attempt_number in self.D_n:
                    self.D_n[node.cts_message.rts_attempt_number] += node.finished_at
                    self.D_n_counter[node.cts_message.rts_attempt_number] += 1
                else:
                    self.D_n[node.cts_message.rts_attempt_number] = node.finished_at
                    self.D_n_counter[node.cts_message.rts_attempt_number] = 1
        for key, value in self.D_n.items():
            self.D_n[key] = self.D_n[key] / self.D_n_counter[key]

        # ratio between rts transmision time and total time
        if self.time != 0:
            self.p_rts_collision_to_data = (self.gateway.total_working_time - self.gateway.blocked_time) / (self.time)
        else:
            self.p_rts_collision_to_data = 0

        # false success
        self.gateway.stat_hidden_block = len(self.gateway.successful_processed_rts_messages) - self.nodes_count_that_transmitted_data


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
            if node.ack_message is None \
                    and (self.input.N_retry is not None
                         and node.is_active):
                return False
        return True

    def update_time(self):
        """
        Find next event time
        """
        t1 = self.get_first_rts_generation_time()
        t2 = self.get_first_rts_transmission_time()
        t3 = self.get_first_cts_arrived_to_node_time()
        t4 = self.get_first_rts_arrived_to_gw_time()
        t5 = self.get_ack_time()

        times = []
        if t1 is not None: times.append(t1)
        if t2 is not None: times.append(t2)
        if t3 is not None: times.append(t3)
        if t4 is not None: times.append(t4)
        if t5 is not None: times.append(t5)

        if not times:
            if self.input.is_debug:
                print("Seems all the Nodes have transmitted data or exceeded retry limit")
                print("Simulation should be finished")
        else:
            t = min(times)

            if self.input.is_debug:
                if t1 is not None and t == t1: event = "RTS generation processing"
                if t2 is not None and t == t2: event = "RTS transmission processing"
                if t3 is not None and t == t3: event = "CTS arrive processing"
                if t4 is not None and t == t4: event = "RTS arrive processing"
                if t5 is not None and t == t5: event = "ACK processing"

                print("Next event is", event, "at", t)
                print("----------")
            self.time = t

    def get_ack_time(self):
        time = None
        if self.gateway.send_ack_at is not None:
            time = self.gateway.send_ack_at
        return time

    def get_first_rts_generation_time(self):
        """
        Find the time for the next RTS generation
        """

        time = None
        for node in self.nodes:
            if node.ack_message is not None:
                continue
            if self.input.N_retry is not None and not node.is_active:
                continue
            if node.next_rts_generation_time is not None:
                if time is None or time > node.next_rts_generation_time:
                    time = node.next_rts_generation_time
        return time

    def get_first_rts_transmission_time(self):
        """
        Find the time for the next RTS transmission
        """

        time = None
        for node in self.nodes:
            if node.ack_message is not None:
                continue

            for key, rts in node.ready_to_transmit_rts.items():
                if rts.sent_from_node_at is not None:
                    if time is None or time > rts.sent_from_node_at:
                        time = rts.sent_from_node_at
        return time

    def get_first_cts_arrived_to_node_time(self):
        """
        Find the time for the next arriving CTS
        """

        time = None
        for node in self.nodes:

            if node.ack_message is not None:
                continue
            if self.input.N_retry is not None and not node.is_active:
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
        for key, rts in self.gateway.rts_messages_to_be_processed.items():
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
                  ", rts failure =", len(self.gateway.unsuccessful_processed_rts_messages))
            for node in self.nodes:
                print("     Node", node.id, ": data sent =", node.ack_message is not None, ",ready to sent rts =",
                      len(node.ready_to_transmit_rts), ",sent rts =",
                      len(node.transmitted_rts_messages), ", received cts =", len(node.received_cts_messages),
                      ", transmission attempt =", node.transmission_attempt, ", retry limit =", self.input.N_retry,
                      ", waiting for other data transmission finished=", node.waiting_for_other_data_transmission_finished)
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
                    cts_receiving_map[node.cts_message.arrived_at] = "Node " + str(
                        node.id) + " will process CTS at " + str(
                        node.cts_message.arrived_at)

            rts_arrived_at_gateway_map = {}
            rts_processed_at_gateway_map = {}
            for key, rts in self.gateway.rts_messages_to_be_processed.items():
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
                for elem in sorted(rts_arrived_at_gateway_map.items()):
                    print("         ", elem[1])
            if rts_processed_at_gateway_map:
                print("     RTS processing:")
                for elem in sorted(rts_processed_at_gateway_map.items()):
                    print("         ", elem[1])
            print()
