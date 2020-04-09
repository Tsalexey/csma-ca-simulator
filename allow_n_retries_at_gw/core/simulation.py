from allow_n_retries_at_gw.core.gateway import Gateway
from allow_n_retries_at_gw.core.node import Node


class Simulation:
    def __init__(self, nodes_count, distance_to_gateway, is_debug):
        self.is_debug = is_debug
        self.nodes_count = nodes_count
        self.distance_to_gateway = distance_to_gateway

        print("Generate nodes:")

        self.nodes = []
        for i in range(int(nodes_count)):
            self.nodes.append(Node(i, self.nodes_count, True))

        print("Generate gateway:")
        self.gateway = Gateway(True)

    def run(self):
        if self.is_debug:
            print()
            print("# Simulation started")
            print()
        self.time = 0.0
        self.retry_number = 0

        # send beacon message
        self.gateway.send_beacon_message()

        # receive beacon message on nodes
        for node in self.nodes:
            node.receive_beacon_message(self.time)

        # order nodes by beacon receiving time
        self.order_nodes_by_beacon_receiving_time()

        while self.retry_number <= 3:
            print("Retry #", self.retry_number, "\n")
            for node in self.nodes:
                node.wait_before_sending_rts(self.retry_number)
                node.send_rts()
            self.order_nodes_by_rts_sending_time()
            self.order_nodes_by_rts_receiving_time()
            self.time = self.nodes[0].rts_receiving_time
            self.retry_number = self.retry_number + 1
            if self.is_debug:
                print("time: ", self.time)
                print()

            if self.checkForCollisions() == False:
                break

        if self.is_debug:
            print()
            print("There was ", self.retry_number-1, " retry attempts")
            print()
            print("# Simulation ended")

    def checkForCollisions(self):
        has_collisions = False
        rts_processing_time = 1

        if self.is_debug:
            print("Check for collisions within RTS processing time = ", rts_processing_time)

        collisioning_pairs = {}

        node_i = self.nodes[0]
        for node_j in self.nodes:
            t1 = node_i.rts_receiving_time
            t2 = node_j.rts_receiving_time
            if node_i.id != node_j.id and collisioning_pairs.get(node_j.id) is None and max(t1, t2) - min(t1, t2) <= rts_processing_time:
                has_collisions = True
                collisioning_pairs[node_j.id] = node_i.id
                collisioning_pairs[node_i.id] = node_j.id
                if self.is_debug:
                    print("Collision detected between nodes ", node_j.id, " and ", node_i.id, ", collision duration =", rts_processing_time - (max(t1, t2) - min(t1, t2)))
        if self.is_debug:
            print()
        return has_collisions

    def order_nodes_by_beacon_receiving_time(self):
        self.nodes.sort(key=get_node_beacon_receive_time)
        if self.is_debug:
            print("\nOrder nodes by beacon receive time")
            for node in self.nodes:
                print("     Node{id=", node.id, ", beacon receive time =", node.beacon_receive_time, "}")
            print()

    def order_nodes_by_rts_sending_time(self):
        self.nodes.sort(key=get_node_rts_sending_time)
        if self.is_debug:
            print("Order nodes by rts sending time")
            for node in self.nodes:
                print("     Node{id =", node.id, ", rts sending time =", node.rts_sending_time, "}")
            print()

    def order_nodes_by_rts_receiving_time(self):
        self.nodes.sort(key=get_node_rts_receiving_time)
        if self.is_debug:
            print("Order nodes by rts receiving time")
            for node in self.nodes:
                print("     Node{id =", node.id, ", rts sending time =", node.rts_receiving_time, "}")
            print()


def get_node_beacon_receive_time(node):
    return node.beacon_receive_time

def get_node_rts_sending_time(node):
    return node.rts_sending_time

def get_node_rts_receiving_time(node):
    return node.rts_receiving_time
