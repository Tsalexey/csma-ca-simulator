import time


class D_n_analytic:
    def __init__(self, data, retry_upper_bound):
        self.data = data
        if retry_upper_bound is None:
            self.retry_upper_bound = 2000
        else:
            self.retry_upper_bound = retry_upper_bound

    def calculate(self):
        D_analytic = {}

        # just limiting N_retry with a big number because of summing to Inf is impossible
        rts_retry = self.data.N_retry
        if rts_retry is None:
            rts_retry = self.retry_upper_bound

        for n in range(1, rts_retry + 1):
            t1 = time.time()
            sum_t_w = 0.0

            for m in range(1, n + 1):
                sum_t_w += self.data.T_max / 2  # mean value for uniform random distribution

            D_analytic[n] = self.data.tau_g_beacon + \
                            self.data.tau_p_max + \
                            (n - 1) * self.data.tau_out + \
                            n * (self.data.tau_g_rts + self.data.tau_p_max) + \
                            sum_t_w + \
                            self.data.tau_g_cts + self.data.tau_p_max + \
                            self.data.tau_g_data + self.data.tau_p_max + \
                            self.data.tau_g_ack + self.data.tau_p_max

            t2 = time.time()
            print("     ", n, "retry, D(", n, ")=", D_analytic[n], ", executed in %s seconds" % (t2 - t1))
        return D_analytic