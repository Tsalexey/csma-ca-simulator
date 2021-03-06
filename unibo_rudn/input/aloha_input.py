
class AlohaInput:
    def __init__(self):
        self.is_debug = False
        self.auto_continue = True
        self.is_debug_cycle_info = False
        self.is_debug_cycle_error = False
        self.is_debug_node_info = False

        self.sensing = False
        self.refrain_from_transmit = False
        self.repeats = 3

        self.simulation_time = 0.000001 # seconds

        self.Nretx = 3  # retransmission attemps, None = unlimited
        self.NN = 50 # nodes number
        self.p_a = 1.0 # probability that node has RTS message to transmit

        self.B = 100 * pow(10, 9) # Bandwidth
        self.eta = 1 # Spectral Efficiency
        self.rb = self.B * self.eta  # Bit rate

        self.sphere_radius = 2 # meter
        self.c = 3 * pow(10, 8) # meters/second - light speed

        # message length
        self.Ldata = 0 # do not use for ALOHA
        self.Ldatapay = 0 # do not use for ALOHA
        self.Lack = 0 # do not use for ALOHA
        self.Lrts = 20 # Bytes - ALOHA DATA
        self.Lcts = 2 # Bytes - ALOHA ACK
        self.Lbeacon = 00 # do not use for ALOHA

        # times
        # self.tau_p_max = 0 # self.sphere_radius / self.c # sec - maximal propagation time
        self.Tslot = pow(10, -9)

        self.Tdata = 0#(self.Ldata * 8) / self.rb
        self.Tack = 0#(self.Lack * 8) / self.rb
        self.Trts = pow(10, -9) #(self.Lrts * 8) / self.rb
        self.Tcts = pow(10, -9) #(self.Lcts * 8) / self.rb
        self.Tbeacon = 0#(self.Lbeacon * 8) / self.rb
        self.Tbo = pow(10, -9) #(self.Lcts * 8) / self.rb
        self.Tout = pow(10, -9) #self.Tcts
        self.Tidle = pow(10, -9) #self.Tcts # o be set according to the Application - it could be also zero
        self.Trft = 0
        self.Twait = 00
        self.Tmax = 12 # parameter of the mathematical model

        self.print()

    def generate_output_filename(self, file_name):
        return "../results/" \
               + file_name \
               + "_pa[" + str(self.p_a) + "]" \
               + "_sensing[" + str(self.repeats) + "]" \
               + "_nodes[" + str(1) + "-" + str(self.NN) + "]" \
               + "_radius[" + str(self.sphere_radius) + "]" \
               + "_retry[" + str(self.Nretx) + "]" \
               + "_repeats[" + str(self.repeats) + "]" \
               + "_time[" + str(self.simulation_time) + "].csv"

    def print(self):
        print("Input parameters:")
        print("     sensing - ", self.sensing)
        print("     Nretx - ", self.Nretx)
        print("     NN - ", self.NN)
        print("     p_a - ", self.p_a)
        print("     Tdata - ", self.Tdata * pow(10, 9), " ns")
        print("     Tack - ", self.Tack * pow(10, 9), " ns")
        print("     Trts - ", self.Trts * pow(10, 9), " ns")
        print("     Tcts - ", self.Tcts * pow(10, 9), " ns")
        print("     Tbeacon - ", self.Tbeacon * pow(10, 9), " ns")
        print("     Tbo - ", self.Tbo * pow(10, 9), " ns")
        print("     Tout - ", self.Tout * pow(10, 9), " ns")
        print("     Tidle - ", self.Tidle * pow(10, 9), " ns")
        print("     Twait - ", self.Twait * pow(10, 9), " ns")
        print("     Tmax - ", self.Tmax)
        print("")