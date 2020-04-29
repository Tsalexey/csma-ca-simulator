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

        self.successful_processed_rts_messages = []
        self.unsuccessful_processed_rts_messages = []
        self.rts_messages_to_be_processed = []

        self.received_rts_count = 0

        self.blocked_time = 0.0;
        self.total_working_time = 0.0;

        if self.is_debug:
            print("# Generate gateway{x =", self.position.x, ", y = ", self.position.y, ", z = ", self.position.z, "}")

    def push_rts(self, rts_message):
        rts_message.processed_at_gateway_at = rts_message.arrived_to_gateway_at
        self.rts_messages_to_be_processed.append(rts_message)
        self.order_rts_by_arriving_time()

    def order_rts_by_arriving_time(self):
        self.rts_messages_to_be_processed.sort(key=get_rts_arrived_to_gateway_time)

def get_rts_arrived_to_gateway_time(rts_message):
    return rts_message.arrived_to_gateway_at