
class Case3Input:
    def __init__(self):
        self.is_debug = False
        self.auto_continue = True
        self.is_debug_cycle_info = False
        self.is_debug_cycle_error = False
        self.is_debug_node_info = False

        self.sensing = True
        self.refrain_from_transmit = False
        self.repeats = 100

        self.simulation_time = 10000 # seconds

        self.Nretx = 3 # retransmission attemps, None = unlimited
        self.NN = 10 # nodes number
        self.start_from = 1
        self.p_a = 1.0 # probability that node has RTS message to transmit

        self.B = 100 * pow(10, 9) # Bandwidth
        self.eta = 0.5 # Spectral Efficiency
        self.rb = self.B * self.eta  # Bit rate

        self.sphere_radius = 2 # meter
        self.c = 3 * pow(10, 8) # meters/second - light speed

        # message length
        self.Ldata = 3 # Bytes data total
        self.Ldatapay = 2 # Bytes payload data
        self.Lack = 3 # Bytes
        self.Lrts = 3 # Bytes
        self.Lcts = 3 # Bytes
        self.Lbeacon = 3 # Bytes

        # times
        # self.tau_p_max = 0 # self.sphere_radius / self.c # sec - maximal propagation time
        self.time_multiplier = 1 # for ns use pow(10, -9)

        self.Tslot = 3 * self.time_multiplier # self.Lbeacon * 8) / self.rb
        self.Tdata = 30 * self.time_multiplier # (self.Ldata * 8) / self.rb
        self.Tack = 3 * self.time_multiplier # (self.Lack * 8) / self.rb
        self.Trts = 3 * self.time_multiplier # (self.Lrts * 8) / self.rb
        self.Tcts = 3 * self.time_multiplier # (self.Lcts * 8) / self.rb
        self.Tbo = 3 * self.time_multiplier # (self.Lcts * 8) / self.rb
        self.Tout = self.Tdata + self.Tack #self.Trts
        self.Tidle = 3 * self.time_multiplier
        self.Twait = self.Tdata + self.Tack
        self.Trft = self.Tdata + self.Tack
        self.Tmax = 12 # parameter of the mathematical model

        self.print()

    def generate_output_filename(self, file_name):
        return "../results/" \
               + file_name \
               + "_pa[" + str(self.p_a) + "]" \
               + "_sensing[" + str(self.sensing) + "]" \
               + "_refrain[" + str(self.refrain_from_transmit) + "]" \
               + "_nodes[" + str(self.start_from) + "-" + str(self.NN) + "]" \
               + "_radius[" + str(self.sphere_radius) + "]" \
               + "_retry[" + str(self.Nretx) + "]" \
               + "_repeats[" + str(self.repeats) + "]" \
               + "_time[" + str(self.simulation_time) + "].csv"

    def print(self):
        print("Input parameters:")
        print("     sensing - ", self.sensing)
        print("     refrain from transmit - ", self.refrain_from_transmit)
        print("     Nretx - ", self.Nretx)
        print("     NN - ", self.NN)
        print("     p_a - ", self.p_a)
        print("     Tdata - ", self.Tdata * self.time_multiplier)
        print("     Tack - ", self.Tack * self.time_multiplier)
        print("     Trts - ", self.Trts * self.time_multiplier)
        print("     Tcts - ", self.Tcts * self.time_multiplier)
        print("     Tbo - ", self.Tbo * self.time_multiplier)
        print("     Tout - ", self.Tout * self.time_multiplier)
        print("     Tidle - ", self.Tidle * self.time_multiplier)
        print("     Twait - ", self.Twait * self.time_multiplier)
        print("     Trft - ", self.Trts * self.time_multiplier)
        print("     Tmax - ", self.Tmax)
        print("")