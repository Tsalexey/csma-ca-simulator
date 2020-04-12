from unibo_rudn.core.gateway import Gateway
from unibo_rudn.core.node import Node


class Simulation:
    def __init__(self, nodes_count,
                 distance_to_gateway,
                 T_max,
                 rts_generation_intensity,
                 t_out,
                 retry_limit,
                 rts_processing_duration,
                 cts_channel_busy_time,
                 is_debug,
                 auto_continue):

        self.is_debug = is_debug
        self.nodes_count = nodes_count
        self.distance_to_gateway = distance_to_gateway
        self.auto_continue = auto_continue
        # Node parameters
        self.T_max = T_max
        self.rts_generation_intensity = rts_generation_intensity
        self.t_out = t_out
        self.retry_limit = retry_limit
        # Gateway parameters
        self.rts_processing_duration = rts_processing_duration
        self.cts_channel_busy_time = cts_channel_busy_time
        # Statistics
        self.collision_duration = 0.0
        self.collision_blocking_probability = 0.0

        if self.is_debug:
            print("# Generate nodes:")

        self.nodes = []
        for i in range(1, nodes_count + 1):
            self.nodes.append(Node(i, self.nodes_count, self.T_max, self.rts_generation_intensity, self.t_out, self.retry_limit, self.is_debug))

        if self.is_debug:
            print("# Generate gateway:")

        self.gateway = Gateway(self.rts_processing_duration, self.cts_channel_busy_time, self.is_debug)

    def run(self):
        if self.is_debug:
            print("\n# Simulation started\n")

        self.time = 0.0
        while not self.is_simulation_finished():
            if self.is_debug:
                print("[*] Time", self.time)
                self.debug_run()
                self.debug_next_event_times(5)

            if self.time == 0.0:
                if self.is_debug:
                    print("It is time to generate Beacon at gateway")
                beacon_message = self.gateway.generate_beacon_message(self.time)
                for node in self.nodes:
                    node.push_beacon_message(beacon_message)
                    if self.is_debug:
                        print("     Node", node.id, "will receive beacon at", node.beacon_message.arrived_to_node_at)
            else:
                for node in self.nodes:
                    if not node.is_user_data_sent:
                        if self.time == node.next_rts_generation_time:
                            if self.is_debug:
                                print("It is time to generate RTS for Node", node.id)
                            rts_generation_time = node.next_rts_generation_time
                            node.generate_rts_message()
                            if self.is_debug:
                                print("Node", node.id, "has generated RTS at", rts_generation_time,", RTS will be sent at", node.last_generated_rts_message.sent_from_node_at)
                        if node.last_generated_rts_message is not None and self.time == node.last_generated_rts_message.sent_from_node_at:
                            if self.is_debug:
                                print("It is time to send RTS for Node", node.id)
                            sent_from_node_at = node.last_generated_rts_message.sent_from_node_at
                            node.sent_rts_messages.append(node.last_generated_rts_message)
                            self.gateway.push_rts(node.last_generated_rts_message)
                            node.last_generated_rts_message = None
                            if self.is_debug:
                                print("Node", node.id, "has sent RTS message at", sent_from_node_at )
                        if node.cts_message is not None and self.time == node.cts_message.arrived_to_node_at:
                            if self.is_debug:
                                print("It is time to process CTS for Node", node.cts_message.id, "by Node", node.id)
                            node.next_rts_generation_time = node.cts_message.arrived_to_node_at + node.cts_message.channel_busy_time
                            node.received_cts_messages.append(node.cts_message)
                            if node.cts_message.id == node.id:
                                node.is_user_data_sent = True
                                node.next_rts_generation_time = None
                                node.last_generated_rts_message = None
                            else:
                                node.last_generated_rts_message = None
                                node.cts_message = None

                self.gateway.order_rts_by_arriving_time()
                for index, rts in enumerate(self.gateway.rts_messages_to_be_processed):
                    if self.time == rts.arrived_to_gateway_at:
                        if self.is_debug:
                            print("It is time to process RTS at Gateway")
                        arrive_time = rts.arrived_to_gateway_at
                        service_end_time = arrive_time + self.gateway.rts_processing_duration
                        collision_rts_list = []
                        collision_ids = []
                        for other_index, other_rts in enumerate(self.gateway.rts_messages_to_be_processed):
                            if index != other_index and service_end_time >= other_rts.arrived_to_gateway_at:
                                collision_rts_list.append(other_rts)
                                collision_ids.append(other_rts.id)
                                if self.is_debug:
                                    if len(collision_ids) == 1:
                                        print("Node", rts.id, "arrived to gateway at", rts.arrived_to_gateway_at, "and finishes processing at", rts.arrived_to_gateway_at + self.gateway.rts_processing_duration)
                                    print("Node", other_rts.id, "arrive to gateway at", other_rts.arrived_to_gateway_at, "and finishes processing at", other_rts.arrived_to_gateway_at + self.gateway.rts_processing_duration)
                        if collision_rts_list:
                            collision_rts_list.append(rts)
                            self.collision_duration += service_end_time - arrive_time
                            if self.is_debug:
                                print("There is a collision between RTS from node", rts.id, "and", collision_ids)
                                print("Collision time", service_end_time - arrive_time)
                            self.gateway.unsuccessful_processed_rts_messages.append(collision_rts_list)
                            self.gateway.rts_messages_to_be_processed = list(filter(lambda v: v not in collision_rts_list, self.gateway.rts_messages_to_be_processed))
                        else:
                            self.gateway.rts_messages_to_be_processed.remove(rts)
                            self.gateway.successful_processed_rts_messages.append(rts)
                            cts_message = self.gateway.generate_cts_message(self.time)
                            cts_message.id = rts.id
                            if self.is_debug:
                                print("CTS is sent by gateway at", cts_message.sent_from_gateway_at)
                            for node in self.nodes:
                                node.push_cts_message(cts_message)
                                if self.is_debug:
                                    print("Node", node.id, "will receive CTS at", node.cts_message.arrived_to_node_at)

            # update statistics
            if self.time != 0.0:
                self.collision_blocking_probability = self.collision_duration / self.time
            # find next event and update system time
            self.update_time()
        if self.is_debug:
            print("\n# Simulation ended at", self.time)
            self.debug_run()

    def is_simulation_finished(self):
        if self.is_debug:
            print("Gateway has no more rts to process =", self.gateway_has_no_more_rts_to_process())
            if self.retry_limit is None:
                print("RTS transmitted by all the nodes =", self.is_rts_transmitted_by_all_nodes())
            else:
                print("All Nodes exhausted retry limit =", self.is_all_nodes_exhausted_retry_limit())

        if self.retry_limit is None:
            return self.gateway_has_no_more_rts_to_process() and self.is_rts_transmitted_by_all_nodes()
        else:
            return self.gateway_has_no_more_rts_to_process() and self.is_all_nodes_exhausted_retry_limit()


    def gateway_has_no_more_rts_to_process(self):
        return len(self.gateway.rts_messages_to_be_processed) == 0

    def is_rts_transmitted_by_all_nodes(self):
        for node in self.nodes:
            if node.is_user_data_sent == False and node.retry_limit is None:
                return False
        return True

    def is_all_nodes_exhausted_retry_limit(self):
        for node in self.nodes:
            if node.is_user_data_sent == False and node.retry_limit is not None and len(node.sent_rts_messages) < node.retry_limit:
                return False
        return True

    def update_time(self):
        t1 = self.get_first_rts_generation_time()
        t2 = self.get_first_rts_send_from_node_time()
        t3 = self.get_first_cts_arrived_to_node_time()
        t4 = self.get_first_rts_arrived_to_gw_time()

        times = []
        if t1 is not None: times.append(t1)
        if t2 is not None: times.append(t2)
        if t3 is not None: times.append(t3)
        if t4 is not None: times.append(t4)

        if not times:
            if self.is_debug:
                print("It looks like all Nodes have transmitted user data or exhausted retransmision limit, so simulation should be finished")
        else:
            t = min(times)

            if self.is_debug:
                if t1 is not None and t == t1: event = "RTS generation"
                if t2 is not None and t == t2: event = "RTS sending"
                if t3 is not None and t == t3: event = "CTS processing"
                if t4 is not None and t == t4: event = "RTS processing"
                print("Next event is", event, "at", t)
                print("----------")
            self.time = t

    def get_first_rts_generation_time(self):
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
        time = None
        for rts in self.gateway.rts_messages_to_be_processed:
            if rts.arrived_to_gateway_at is not None and time is None:
                time = rts.arrived_to_gateway_at
            if time > rts.arrived_to_gateway_at:
                time = rts.arrived_to_gateway_at
        return time

    def debug_run(self):
        if self.is_debug:
            print("[*] System state is:")
            print("     Gateway: rts to handle =", len(self.gateway.rts_messages_to_be_processed),
                  ", rts success=", len(self.gateway.successful_processed_rts_messages),
                  ", rts failure =", len(self.gateway.unsuccessful_processed_rts_messages),
                  ", collision time=", self.collision_duration,
                  ", collision prob = ", self.collision_blocking_probability)
            for node in self.nodes:
                print("     Node", node.id, ": data sent =", node.is_user_data_sent, ",sent rts =", len(node.sent_rts_messages), ", received cts =", len(node.received_cts_messages), ", retry number =", node.retry_number, ", retry limit =", node.retry_limit)
        if self.is_debug and not self.auto_continue:
            print()
            user_input = input("[?] Press Enter in order to continue or input 'True' to enabled auto continue mode: ")
            if bool(user_input) == True:
                self.auto_continue = True

    def debug_next_event_times(self, events_count):
        if self.is_debug:
            rts_generation_map = {}
            rts_sending_map = {}
            cts_receiving_map = {}
            for node in self.nodes:
                if node.next_rts_generation_time is not None:
                    rts_generation_map[node.next_rts_generation_time] = "Node " + str(node.id) + " will generate new RTS at " + str(node.next_rts_generation_time)
                if node.last_generated_rts_message is not None:
                    rts_sending_map[node.last_generated_rts_message.sent_from_node_at] = "Node " + str(node.id) + " will send RTS at " + str(node.last_generated_rts_message.sent_from_node_at)
                if node.cts_message is not None:
                    cts_receiving_map[node.cts_message.arrived_to_node_at] = "Node " + str(node.id) + " will process CTS at " + str(node.cts_message.arrived_to_node_at)

            rts_arrived_at_gateway_map = {}
            rts_processed_at_gateway_map = {}
            for rts in self.gateway.rts_messages_to_be_processed:
                rts_arrived_at_gateway_map[rts.arrived_to_gateway_at] = "RTS from Node " + str(rts.id) + " will arrive to gateway at " + str(rts.arrived_to_gateway_at)
                rts_processed_at_gateway_map[rts.processed_at_gateway_at] = "RTS from Node " + str(rts.id) + " processing  will be finished at " + str(rts.processed_at_gateway_at)

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
