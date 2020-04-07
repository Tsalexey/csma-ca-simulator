from core.position import Position


class Gateway:
    def __init__(self, is_debug):
        self.is_debug = is_debug
        self.position = Position(0.0)
        print("Gateway{x =", self.position.x, ", y = ", self.position.y, ", z = ", self.position.z, "}")

    def send_beacon_message(self):
        if self.is_debug:
            print("Gateway has generated beacon message")
