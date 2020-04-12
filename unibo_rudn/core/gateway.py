from unibo_rudn.core.Messages import BeaconMessage, CTSMessage
from unibo_rudn.core.position import Position


class Gateway:
    def __init__(self, rts_processing_duration, cts_channel_busy_time, is_debug):
        self.is_debug = is_debug
        self.position = Position(0.0)
        self.rts_processing_duration = rts_processing_duration
        self.cts_channel_busy_time = cts_channel_busy_time

        self.successful_processed_rts_messages = []
        self.unsuccessful_processed_rts_messages = []
        self.rts_messages_to_be_processed = []

        if self.is_debug:
            print("Gateway{x =", self.position.x, ", y = ", self.position.y, ", z = ", self.position.z, "}")

    def generate_beacon_message(self, time):
        if self.is_debug:
            print("Gateway generated Beacon at ", time)
        return BeaconMessage("Gateway", time)

    def generate_cts_message(self, time):
        return CTSMessage("Gateway", time, self.cts_channel_busy_time)

    def push_rts(self, rts_message):
        rts_message.processed_at_gateway_at = rts_message.arrived_to_gateway_at + self.rts_processing_duration
        self.rts_messages_to_be_processed.append(rts_message)
        self.order_rts_by_arriving_time()

    def order_rts_by_arriving_time(self):
        self.rts_messages_to_be_processed.sort(key=get_rts_arrived_to_gateway_time)

def get_rts_arrived_to_gateway_time(rts_message):
    return rts_message.arrived_to_gateway_at