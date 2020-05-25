from unibo_rudn.core.Messages import BeaconMessage, CTSMessage
from unibo_rudn.core.position import Position


class Gateway:
    def __init__(self, tau_g_beacon, cts_transmision_time, ack_transmition_time, cts_channel_busy_time, is_debug):
        self.is_debug = is_debug
        self.position = Position(0.0)

        self.tau_g_beacon = tau_g_beacon
        self.cts_transmision_time = cts_transmision_time
        self.cts_channel_busy_time = cts_channel_busy_time
        self.ack_transmition_time = ack_transmition_time

        self.send_ack_at = None
        self.send_ack_to = None

        self.last_ack_time = None

        self.total_processed_rts_messages = {}
        self.successful_processed_rts_messages = {}
        self.unsuccessful_processed_rts_messages = {}

        self.rts_messages_to_be_processed = {}
        self.rts_received_after_cts = {}

        self.cts_transmitted_to = {}
        self.received_rts_count = 0

        self.number_of_collisions = 0

        self.stat_hidden_block = []

        self.blocked_time = 0.0;
        self.total_working_time = 0.0;

        self.start_serving_time = 0.0
        self.end_serving_time = 0.0
        self.busy_time = 0.0

        if self.is_debug:
            print("# Generate gateway{x =", self.position.x, ", y = ", self.position.y, ", z = ", self.position.z, "}")

    def order_rts_by_arriving_time(self):
        self.rts_messages_to_be_processed.sort(key=get_rts_arrived_to_gateway_time)

def get_rts_arrived_to_gateway_time(rts_message):
    return rts_message.arrived_to_gateway_at