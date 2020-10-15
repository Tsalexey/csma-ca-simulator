from unibo_rudn.core.simulation_type import SimulationType


class RealisticInput1:
    def __init__(self):
        self.is_debug = False
        self.auto_continue = True
        self.is_debug_cycle_info = False
        self.is_debug_cycle_error = False

        self.time_limit = True # if False then run simulation until the error between cycle time of all nodes is greater then self.precision
        self.precision = 0.001

        self.sensing = True
        self.repeats = 1
        self.mode = SimulationType.CYCLIC

        # self.planned_success = 25
        # 0.001 = 333 real minutes for 1-50 nodes
        # 0.0002 = 60 real minutes for 1-50 nodes
        # 0.0001 = 30 real minutes for 1-50 nodes
        # 0.00005 = 15 real minutes for 1-50 nodes
        self.simulation_time = 0.00001 # seconds

        self.Nretx = 3  # retransmission attemps, None = unlimited
        self.NN = 20 # nodes number
        self.p_a = 1.0 # probability that node has RTS message to transmit

        self.B = 100 * pow(10, 9) # Bandwidth
        self.eta = 0.5 # Spectral Efficiency
        self.rb = self.B * self.eta  # Bit rate

        self.sphere_radius = 2 # meter
        self.c = 3 * pow(10, 8) # meters/second - light speed

        # message length
        self.Ldata = 100 # Bytes data total
        self.Ldatapay = 90 # Bytes payload data
        self.Lack = 10 # Bytes
        self.Lrts = 10 # Bytes
        self.Lcts = 10 # Bytes
        self.Lbeacon = 10 # Bytes

        # times
        # self.tau_p_max = 0 # self.sphere_radius / self.c # sec - maximal propagation time
        self.Tdata = (self.Ldata * 8) / self.rb
        self.Tack = (self.Lack * 8) / self.rb
        self.Trts = (self.Lrts * 8) / self.rb
        self.Tcts = (self.Lcts * 8) / self.rb
        self.Tbeacon = (self.Lbeacon * 8) / self.rb
        self.Tbo = (self.Lcts * 8) / self.rb
        self.Tdatacts = self.Tcts + self.Tdata + self.Tack
        self.Tout = self.Tcts
        self.Tidle = self.Trts # o be set according to the Application - it could be also zero
        self.Twait = self.Tdata + self.Tack
        self.Tmax = 12 # parameter of the mathematical model

