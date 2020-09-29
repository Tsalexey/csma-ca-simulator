from unibo_rudn.core.simulation_type import SimulationType


class InputDiscreteTime:
    def __init__(self):
        self.is_debug = False
        self.is_debug_cycle_info = False
        self.auto_continue = True
        self.sensing = False
        self.repeats = 1
        self.mode = SimulationType.CYCLIC
        self.simulation_time = 10000

        self.NN = 20

        self.p_a = 1.0 # probability that node has RTS message to transmit

        self.sphere_radius = 2 # meter
        self.Nretx = 3  # allowed rts retransmission count, None = unlimited
        self.T_beam = 2 # sec - time of time slot

        self.rb = 53687091200 # 50Gbit/sec - channel bandwidth
        self.c = 3 * pow(10, 8) # meters/second - light speed

        # message length
        self.N_beacon = 20*8 # bit - length of BEACON message
        self.N_rts = 20*8 # bit - length of RTS message
        self.N_cts = 20*8 # bit - length of CTS message
        self.N_ack = 20*8 # bit - length of ACK message
        self.N_data = 100*8 # bit - length of user data messsage

        # message transmission time
        self.Tbeacon = 1 # sec - transmission time of BEACON message
        self.Trts = 1 # sec - transmission time of RTS message
        self.Tcts = 1 # sec - transmission time of CTS message
        self.Tack = 1 # sec - transmission time of ACK message
        self.Tdata = 1 # sec - transmission time of user data message

        # other timing estimations

        # if self.Nretx is None:
        #     N = 3.0/2.0
        # else :
        #     N = self.Nretx / 2.0;

        self.N = 12

        self.Tbo = self.N #* self.Trts # sec - delay before sending RTS
        self.tau_p_max = self.sphere_radius / self.c # sec - maximal propagation time
        self.Tout = 2 * self.tau_p_max + self.Tcts # sec - window contention time
        self.tau_channel_busy = self.Tdata \
                                + self.tau_p_max \
                                + self.Tcts \
                                + self.tau_p_max \
                                + self.Tack \
                                + self.tau_p_max # sec - data transmission time


