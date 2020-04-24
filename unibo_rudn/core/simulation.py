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
        self.collision_time_blocking_probability = 0.0
        self.collision_call_blocking_probability = 0.0
        self.time_before_channel_busy = 0
        self.mean_node_finished_at = 0
        self.nodes_count_that_transmitted_data = 0
        self.mean_sent_rts_count = 0

        # gateway
        self.gateway = Gateway(self.input.tau_g_cts, self.input.tau_g_ack, self.input.tau_channel_busy, self.input.is_debug)

        # nodes
        self.nodes = []
        for i in range(1, self.input.nodes_number + 1):
            self.nodes.append(
                Node(i, self.input.sphere_radius, self.input.T_max, self.input.tau_g_rts, self.input.tau_out,
                     self.input.N_retry, self.input.is_debug))

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

            # it is a good time to send beacon message
            if self.time == 0.0:
                if self.input.is_debug:
                    print("It is time to generate Beacon at gateway")
                beacon_message = self.gateway.generate_beacon_message(self.time)
                for node in self.nodes:
                    node.push_beacon_message(beacon_message)
                    if self.input.is_debug:
                        print("     Node", node.id, "will receive beacon at", node.beacon_message.arrived_to_node_at)
            else:
                for node in self.nodes:
                    if not node.is_user_data_sent:

                        # it is time to generate new rts and wait some time before sending
                        if self.time == node.next_rts_generation_time:
                            if self.input.is_debug:
                                print("It is time to generate RTS for Node", node.id)
                            rts_generation_time = node.next_rts_generation_time
                            node.generate_rts_message()
                            if self.input.is_debug:
                                print("Node", node.id, "has generated RTS at", rts_generation_time,
                                      ", RTS will be sent at", node.last_generated_rts_message.sent_from_node_at)

                        # it is time to send rts from node
                        if node.last_generated_rts_message is not None and self.time == node.last_generated_rts_message.sent_from_node_at:
                            if self.input.is_debug:
                                print("It is time to send RTS for Node", node.id)
                            sent_from_node_at = node.last_generated_rts_message.sent_from_node_at
                            node.sent_rts_messages.append(node.last_generated_rts_message)
                            self.gateway.push_rts(node.last_generated_rts_message)
                            node.last_generated_rts_message = None
                            if self.input.is_debug:
                                print("Node", node.id, "has sent RTS message at", sent_from_node_at)

                        # it is time to receive cts from gateway
                        if node.cts_message is not None and self.time == node.cts_message.arrived_to_node_at:
                            if self.input.is_debug:
                                print("It is time to process CTS for Node", node.cts_message.id, "by Node", node.id)
                            node.next_rts_generation_time = node.cts_message.arrived_to_node_at + node.cts_message.channel_busy_time
                            node.received_cts_messages.append(node.cts_message)
                            if node.cts_message.id == node.id:
                                self.gateway.send_ack_at = self.time + node.get_propagation_time() + self.input.tau_g_data
                                self.gateway.send_ack_to = node.id
                                node.cts_message = None
                                node.next_rts_generation_time = None
                                node.last_generated_rts_message = None
                            else:
                                node.last_generated_rts_message = None
                                node.cts_message = None

                # time to receive ack from gateway
                if self.gateway.send_ack_at is not None and self.gateway.send_ack_at == self.time:
                    if self.input.is_debug:
                        print("It is time to send ACK from Gateway")
                    for node in self.nodes:
                        if node.id == self.gateway.send_ack_to:
                            node.is_user_data_sent = True
                            node.finished_at = self.time + node.get_propagation_time() + self.gateway.ack_transmition_time
                            self.gateway.rts_messages_to_be_processed = list(filter(lambda v: v.id != node.id, self.gateway.rts_messages_to_be_processed))
                    self.gateway.send_ack_at = None
                    self.gateway.send_ack_to = None

                # time to finish receiving rts from node
                self.gateway.order_rts_by_arriving_time()
                for index, rts in enumerate(self.gateway.rts_messages_to_be_processed):
                    if self.time == rts.arrived_to_gateway_at:
                        if self.input.is_debug:
                            print("It is time to process RTS at Gateway")

                        possible_collision_end_time = rts.arrived_to_gateway_at
                        possible_collision_start_time = possible_collision_end_time - rts.transmision_time
                        collision_start_time = None

                        collision_rts_list = []
                        collision_ids = []

                        # check for collisions between rts
                        for other_index, other_rts in enumerate(self.gateway.rts_messages_to_be_processed):
                            if index != other_index and possible_collision_end_time >= other_rts.arrived_to_gateway_at - other_rts.transmision_time:

                                if collision_start_time is None:
                                    collision_start_time = other_rts.arrived_to_gateway_at - other_rts.transmision_time
                                else:
                                    if collision_start_time > other_rts.arrived_to_gateway_at - other_rts.transmision_time:
                                        collision_start_time = other_rts.arrived_to_gateway_at - other_rts.transmision_time

                                collision_rts_list.append(other_rts)
                                collision_ids.append(other_rts.id)

                                if self.input.is_debug:
                                    if len(collision_ids) == 1:
                                        print("Node", rts.id, "arrived to gateway at", rts.arrived_to_gateway_at,
                                              "and finishes transmision at",
                                              rts.arrived_to_gateway_at)
                                    print("Node", other_rts.id, "arrive to gateway at", other_rts.arrived_to_gateway_at,
                                          "and finishes processing at",
                                          other_rts.arrived_to_gateway_at)

                        # we got a collision
                        if collision_rts_list:
                            collision_rts_list.append(rts)
                            self.collision_duration += self.input.tau_g_rts
                            if self.input.is_debug:
                                print("There is a collision between RTS from node", rts.id, "and", collision_ids)
                                print("Collision time", possible_collision_end_time - possible_collision_start_time)
                            self.gateway.unsuccessful_processed_rts_messages.append(collision_rts_list)
                            self.gateway.rts_messages_to_be_processed = list(
                                filter(lambda v: v not in collision_rts_list,
                                       self.gateway.rts_messages_to_be_processed))
                        # we got no collisions
                        else:
                            self.gateway.rts_messages_to_be_processed.remove(rts)
                            self.gateway.successful_processed_rts_messages.append(rts)
                            cts_message = self.gateway.generate_cts_message(self.time)
                            cts_message.id = rts.id
                            cts_message.transmision_time = self.gateway.cts_transmision_time
                            if self.input.is_debug:
                                print("CTS is sent by gateway at", cts_message.sent_from_gateway_at)
                            for node in self.nodes:
                                node.push_cts_message(cts_message)
                                if self.input.is_debug:
                                    print("Node", node.id, "will receive CTS at", node.cts_message.arrived_to_node_at)

            # update statistics
            if self.time != 0.0:
                self.collision_time_blocking_probability = self.collision_duration / self.time
            # find next event and update system time
            self.update_time()

        # calculate statistics
        temp_time_before_channel_busy = 0
        temp_finished_at = 0
        temp_nodes_count_that_transmitted_data = 0
        temp_sent_rts = 0

        for node in self.nodes:
            temp_sent_rts += len(node.sent_rts_messages)
            if node.is_user_data_sent:
                temp_nodes_count_that_transmitted_data += 1
                if node.cts_message is not None:
                    temp_time_before_channel_busy += node.cts_message.arrived_to_node_at
                    temp_finished_at+= node.finished_at
        self.time_before_channel_busy += temp_time_before_channel_busy / len(self.nodes)
        self.mean_node_finished_at += temp_finished_at / len(self.nodes)
        self.nodes_count_that_transmitted_data += temp_nodes_count_that_transmitted_data / len(self.nodes)
        self.mean_sent_rts_count += temp_sent_rts / len(self.nodes)
        self.collision_call_blocking_probability = 1 - temp_nodes_count_that_transmitted_data / temp_sent_rts

        if self.input.is_debug:
            print("\n# Simulation ended at", self.time)
            self.debug_run()

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
            if node.is_user_data_sent == False and node.retry_limit is None:
                return False
        return True

    def is_all_nodes_exceeded_retry_limit(self):
        """
        Check if all the nodes transmitted user data (in case of retry limits)
        """

        for node in self.nodes:
            if node.is_user_data_sent == False and node.retry_limit is not None and len(
                    node.sent_rts_messages) < node.retry_limit:
                return False
        return True

    def update_time(self):
        """
        Find next event time
        """
        t1 = self.get_first_rts_generation_time()
        t2 = self.get_first_rts_send_from_node_time()
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
                if t1 is not None and t == t1: event = "RTS generation"
                if t2 is not None and t == t2: event = "RTS sending"
                if t3 is not None and t == t3: event = "CTS processing"
                if t4 is not None and t == t4: event = "RTS processing"
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
        Find time for the next RTS generation
        """
        time = None
        for node in self.nodes:
            if node.is_user_data_sent:
                continue
            if node.retry_limit is not None and len(node.sent_rts_messages) >= node.retry_limit:
                continue
            if node.next_rts_generation_time is not None and time is None:
                time = node.next_rts_generation_time
            if node.next_rts_generation_time is not None and time > node.next_rts_generation_time:
                time = node.next_rts_generation_time
        return time

    def get_first_rts_send_from_node_time(self):
        """
        Find the time for the next departing RTS
        """

        time = None
        for node in self.nodes:
            if node.is_user_data_sent:
                continue
            if node.retry_limit is not None and len(node.sent_rts_messages) >= node.retry_limit:
                continue
            if node.last_generated_rts_message is not None and time is None:
                time = node.last_generated_rts_message.sent_from_node_at
            if node.last_generated_rts_message is not None and time > node.last_generated_rts_message.sent_from_node_at:
                time = node.last_generated_rts_message.sent_from_node_at
        return time

    def get_first_cts_arrived_to_node_time(self):
        """
        Find the time for the next arriving CTS
        """

        time = None
        for node in self.nodes:
            if node.is_user_data_sent:
                continue
            if node.retry_limit is not None and len(node.sent_rts_messages) >= node.retry_limit:
                continue
            if node.cts_message is not None and time is None:
                time = node.cts_message.arrived_to_node_at
            if node.cts_message is not None and time > node.cts_message.arrived_to_node_at:
                time = node.cts_message.arrived_to_node_at
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
                print("     Node", node.id, ": data sent =", node.is_user_data_sent, ",sent rts =",
                      len(node.sent_rts_messages), ", received cts =", len(node.received_cts_messages),
                      ", retry number =", node.retry_number, ", retry limit =", node.retry_limit)
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
                if node.last_generated_rts_message is not None:
                    rts_sending_map[node.last_generated_rts_message.sent_from_node_at] = "Node " + str(
                        node.id) + " will send RTS at " + str(node.last_generated_rts_message.sent_from_node_at)
                if node.cts_message is not None:
                    cts_receiving_map[node.cts_message.arrived_to_node_at] = "Node " + str(
                        node.id) + " will process CTS at " + str(node.cts_message.arrived_to_node_at)

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
