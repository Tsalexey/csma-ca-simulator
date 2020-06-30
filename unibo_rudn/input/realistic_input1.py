from unibo_rudn.core.simulation_type import SimulationType


class RealisticInput1:
    def __init__(self):
        self.is_debug = False
        self.auto_continue = True
        self.sensing = False
        self.repeats = 1
        self.mode = SimulationType.CYCLIC
        self.simulation_time = 0.000001

        self.nodes_number = 5

        self.p_a = 1.0 # probability that node has RTS message to transmit

        self.sphere_radius = 2 # meter
        self.N_retry = 3  # allowed rts retransmission count, None = unlimited
        self.T_beam = 2 # sec - time of time slot

        self.R_b = 53687091200 # 50Gbit/sec - channel bandwidth
        self.c = 3 * pow(10, 8) # meters/second - light speed

        # message length
        self.N_beacon = 20*8 # bit - length of BEACON message
        self.N_rts = 20*8 # bit - length of RTS message
        self.N_cts = 20*8 # bit - length of CTS message
        self.N_ack = 20*8 # bit - length of ACK message
        self.N_data = 100*8 # bit - length of user data messsage

        # message transmission time
        self.tau_g_beacon = self.N_beacon / self.R_b # sec - transmission time of BEACON message
        self.tau_g_rts = self.N_rts / self.R_b # sec - transmission time of RTS message
        self.tau_g_cts = self.N_cts / self.R_b # sec - transmission time of CTS message
        self.tau_g_ack = self.N_ack / self.R_b # sec - transmission time of ACK message
        self.tau_g_data = self.N_data / self.R_b # sec - transmission time of user data message

        # other timing estimations

        # if self.N_retry is None:
        #     N = 3.0/2.0
        # else :
        #     N = self.N_retry / 2.0;

        self.N = 12

        self.T_max = self.N * self.tau_g_rts # sec - delay before sending RTS
        self.tau_p_max = 0 # self.sphere_radius / self.c # sec - maximal propagation time
        self.tau_out = 2 * self.tau_p_max + self.tau_g_cts # sec - window contention time
        self.tau_channel_busy = self.tau_g_data \
                                + self.tau_p_max \
                                + self.tau_g_cts \
                                + self.tau_p_max \
                                + self.tau_g_ack \
                                + self.tau_p_max # sec - data transmission time


