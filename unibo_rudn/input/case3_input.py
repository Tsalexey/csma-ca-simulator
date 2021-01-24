
class Case3Input:
    def __init__(self):
        self.is_debug = False
        self.auto_continue = True
        self.is_debug_cycle_info = False
        self.is_debug_cycle_error = False
        self.is_debug_node_info = False

        self.sensing = True
        self.refrain_from_transmit = False
        self.repeats = 5

        self.simulation_time = 0.000001 # seconds

        self.Nretx = 0  # retransmission attemps, None = unlimited
        self.NN = 50 # nodes number
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

        self.Tslot = pow(10, -9) # self.Lbeacon * 8) / self.rb
        self.Tdata = pow(10, -9) # (self.Ldata * 8) / self.rb
        self.Tack = pow(10, -9) # (self.Lack * 8) / self.rb
        self.Trts = pow(10, -9) # (self.Lrts * 8) / self.rb
        self.Tcts = pow(10, -9) # (self.Lcts * 8) / self.rb
        self.Tbeacon = pow(10, -9) # (self.Lbeacon * 8) / self.rb
        self.Tbo = pow(10, -9) # (self.Lcts * 8) / self.rb
        self.Tout = self.Tdata + self.Tack
        self.Tidle = self.Trts # o be set according to the Application - it could be also zero
        self.Twait = self.Tout
        self.Trft = self.Tdata + self.Tack
        self.Tmax = 12 # parameter of the mathematical model

        self.print()

    def generate_output_filename(self, file_name):
        return "../results/" \
               + file_name \
               + "_pa[" + str(self.p_a) + "]" \
               + "_sensing[" + str(self.sensing) + "]" \
               + "_refrain[" + str(self.refrain_from_transmit) + "]" \
               + "_nodes[" + str(1) + "-" + str(self.NN) + "]" \
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
        print("     Tdata - ", self.Tdata * pow(10, 9), " ns")
        print("     Tack - ", self.Tack * pow(10, 9), " ns")
        print("     Trts - ", self.Trts * pow(10, 9), " ns")
        print("     Tcts - ", self.Tcts * pow(10, 9), " ns")
        print("     Tbeacon - ", self.Tbeacon * pow(10, 9), " ns")
        print("     Tbo - ", self.Tbo * pow(10, 9), " ns")
        print("     Tout - ", self.Tout * pow(10, 9), " ns")
        print("     Tidle - ", self.Tidle * pow(10, 9), " ns")
        print("     Twait - ", self.Twait * pow(10, 9), " ns")
        print("     Trft - ", self.Trts * pow(10, 9), " ns")
        print("     Tmax - ", self.Tmax)
        print("")