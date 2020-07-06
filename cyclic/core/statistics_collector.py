import time

from cyclic.core.simulation import Simulation


class StatisticCollector:

    def __init__(self, input):
        self.input = input
        self.statistics = {}

    def run(self):
        start_time = time.time()

        for i in range(1, self.input.nodes_number + 1):
            t1 = time.time()
            print("Simulation run for ", i, " Nodes, radius", self.input.sphere_radius, ", repeats =", self.input.repeats)

            total_cycle_count = 0.0
            failure_count = 0.0
            success_count = 0.0
            cycle_time = 0.0
            cycle_time2 = 0.0
            rts_time = 0.0
            data_time = 0.0
            channel_busy_time = 0.0
            received_rts = 0.0
            blocked_rts = 0.0
            not_blocked_rts = 0.0
            ignored_rts = 0.0
            blocking_probability_by_call = 0.0

            for j in range(0, self.input.repeats):
                self.input.nodes_number = i
                simulation = Simulation(self.input)
                simulation.run()

                temp_total_cycle_count = 0.0
                temp_failure_count = 0.0
                temp_success_count = 0.0
                temp_cycle_time = 0.0
                temp_cycle_time2 = 0.0
                temp_rts_time = 0.0
                temp_data_time = 0.0
                temp_channel_busy_time = 0.0

                for node in simulation.nodes:
                    temp_total_cycle_count += node.statistics.total_cycle_count
                    temp_failure_count += node.statistics.failure_count
                    temp_success_count += node.statistics.success_count
                    temp_cycle_time += node.statistics.cycle_time
                    temp_cycle_time2 += node.statistics.cycle_time2
                    temp_rts_time += node.statistics.rts_time
                    temp_data_time += node.statistics.data_time
                    temp_channel_busy_time += node.statistics.channel_busy_time

                total_cycle_count += temp_total_cycle_count / len(simulation.nodes)
                failure_count += temp_failure_count / len(simulation.nodes)
                success_count += temp_success_count / len(simulation.nodes)
                cycle_time += temp_cycle_time / len(simulation.nodes)
                cycle_time2 += temp_cycle_time2 / len(simulation.nodes)
                rts_time += temp_rts_time / len(simulation.nodes)
                data_time += temp_data_time / len(simulation.nodes)
                channel_busy_time += temp_channel_busy_time / len(simulation.nodes)

                received_rts += simulation.gateway.statistics.received_rts
                blocked_rts += simulation.gateway.statistics.blocked_rts
                not_blocked_rts += simulation.gateway.statistics.not_blocked_rts
                ignored_rts += simulation.gateway.statistics.ignored_rts
                blocking_probability_by_call += simulation.gateway.statistics.blocking_probability_by_call

            total_cycle_count = total_cycle_count / self.input.repeats
            failure_count = failure_count / self.input.repeats
            success_count = success_count / self.input.repeats
            cycle_time = cycle_time / self.input.repeats
            rts_time = rts_time / self.input.repeats
            data_time = data_time / self.input.repeats
            channel_busy_time = channel_busy_time / self.input.repeats

            received_rts = received_rts / self.input.repeats
            blocked_rts = blocked_rts / self.input.repeats
            not_blocked_rts = not_blocked_rts / self.input.repeats
            ignored_rts = ignored_rts / self.input.repeats
            blocking_probability_by_call = blocking_probability_by_call / self.input.repeats

            self.statistics[i] = [
                i,
                total_cycle_count,
                failure_count,
                success_count,
                pow(10,9)*cycle_time,
                pow(10, 9) *cycle_time2,
                pow(10, 9) *rts_time,
                received_rts,
                blocked_rts,
                not_blocked_rts,
                ignored_rts,
                blocking_probability_by_call,
                (rts_time) / cycle_time,
                0 if cycle_time2 == 0 else (rts_time) / cycle_time2,
                pow(10, 9) * data_time,
                data_time / cycle_time,
                data_time / cycle_time2,
                pow(10, 9) * channel_busy_time,
                channel_busy_time / cycle_time,
                channel_busy_time / cycle_time2
            ]

            t2 = time.time()
            print("     Executed in %s seconds" % (t2 - t1))

        end_time = time.time()
        print("Executed in %s seconds" % (end_time - start_time))

    def debug(self):

        for i in self.statistics.keys():
            print("Nodes = ", i)
            print("     cycles =", self.statistics[i][1])
            print("     failure =", self.statistics[i][2])
            print("     success =", self.statistics[i][3])
            print("     E[tc] =", pow(10,9) * self.statistics[i][4])
            print("     E[tc] 2 =", pow(10,9) * self.statistics[i][5])
            print("     RTS time =", pow(10,9) * self.statistics[i][6])
            print("     received rts= ", self.statistics[i][7])
            print("     blocked rts =", self.statistics[i][8])
            print("     not blocked rts =", self.statistics[i][9])
            print("     ignored rts =", self.statistics[i][10])
            print("     p =", self.statistics[i][11])
            print("     tau =", self.statistics[i][12])
            print("     tau2 =", self.statistics[i][13])
            print("     data time =", pow(10,9) * self.statistics[i][14])
            print("     tau packet =", self.statistics[i][15])
            print("     tau packet 2 =", self.statistics[i][16])

