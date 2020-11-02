

class AlohaInput:
    def __init__(self):
        self.debug_repeats = False
        self.debug_time = False

        self.sensing = False
        self.repeats = 100

        self.slot_time = 2
        self.simulation_time = 10000 * self.slot_time # seconds


        self.Nretx = 3  # retransmission attemps, None = unlimited
        self.NN = 10 # nodes number
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
        self.Lrts = 100 # Bytes - ALOHA DATA
        self.Lcts = 10 # Bytes - ALOHA ACK
        self.Lbeacon = 00 # do not use for ALOHA

        # times
        # self.tau_p_max = 0 # self.sphere_radius / self.c # sec - maximal propagation time
        self.Tdata = 0
        self.Tack = 0
        self.Trts = 10 * self.slot_time
        self.Tcts = self.slot_time
        self.Tbeacon = 0
        self.Tbo = self.slot_time
        self.Tout = self.slot_time
        self.Tidle = self.slot_time
        self.Twait = 0
        self.Tmax = 11

        self.print()


    def print(self):
        print("Input parameters:")

        attrs = vars(self)

        for item in attrs.items():
            print("%s: %s" % item)
        print("")