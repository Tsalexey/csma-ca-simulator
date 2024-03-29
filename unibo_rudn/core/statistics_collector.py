import csv
import time
from enum import Enum

from unibo_rudn.core.simulation import Simulation

class StatisticsType(Enum):
    statistics = "statistics"
    detailed_statistics = "detailed_statistics"

class StatisticCollector:
    def __init__(self, input):
        self.input = input
        self.statistics = {}
        self.detailed_statistics = {}

        self.statistics_description = {
            1 : "Nodes",
            2 : "p_a",
            3: "p{rts_success}",
            4: "p{rts_collision}",
            5: "p{cycle_success}",
            6 : "p{cycle_failure}",
            7 : "p{channel_free}",
            8 : "p{channel_busy}",
            9 : "p{wait}",
            10 : "idle_time",
            11 : "backoff_time",
            12 : "rts_time",
            13 : "cts_time",
            14 : "out_time",
            15 : "data_time",
            16 : "refrain_time",
            17 : "wait_time",
            18 : "Cycle_time",
            19 : "tau",
            20 : "tau_data"
        }

        self.detailed_statistics_description = {
            1 : "Nodes",
            2 : "Total_cycles_count",
            3 : "p{cycle_failure}",
            4 : "p{cycle_success}",
            5 : "Cycle_time_(1rst_approach)",
            6 : "Cycle_time_(2nd_approach)",
            7 : "Cycle_time_(3rd_approach)",
            8 : "Rts_time",
            9 : "Data_time",
            10 : "Wait_time",
            11 : "Channel_busy_time",
            12 : "tau_(1rst_approach)",
            13 : "tau_(2nd_approach)",
            14 : "tau_(3rd_approach)",
            15 : "tau_(4th_approach)",
            16 : "tau_data_(4th_approach)",
            17 : "tau_data_(2nd_approach)",
            18 : "tau_data_(3rd_approach)",
            19 : "tau_data_(4th_approach)",
            20 : "tau_channe_busy_(1rst_approach)",
            21 : "tau_channe_busy_(2nd_approach)",
            22 : "received_rts_msg_count",
            23 : "blocked_rts_msg_count",
            24 : "not_blocked_rts_msg_count",
            25 : "ignored_rts_msg_count",
            26 : "p{collision}",
            27 : "p{wait}"
        }


    def run(self):
        start_time = time.time()

        for i in range(self.input.start_from, self.input.NN + 1):

            t1 = time.time()
            print("Simulation run for ", i, " Nodes, radius", self.input.sphere_radius, ", repeats =", self.input.repeats)

            total_cycle_count = 0.0
            probability_of_rts_success = 0.0
            probability_of_rts_collision = 0.0
            probability_of_channel_free = 0.0
            probability_of_channel_busy = 0.0
            probability_of_failure = 0.0
            probability_of_success = 0.0
            probability_of_wait = 0.0

            cycle_time = 0.0
            cycle_time2 = 0.0
            cycle_time3 = 0.0
            idle_time = 0.0
            backoff_time = 0.0
            rts_time = 0.0
            cts_time = 0.0
            out_time = 0.0
            data_time = 0.0
            wait_time = 0.0
            refrain_time = 0.0
            time_between_tx = 0.0
            not_tx_rx_time = 0.0
            channel_busy_time = 0.0

            simulation_time = 0.0

            total_success_time = 0.0
            total_failure_time = 0.0

            total_idle_time = 0.0
            total_backoff_time = 0.0
            total_rts_time = 0.0
            total_cts_time = 0.0
            total_out_time = 0.0
            total_refrain_time = 0.0
            total_data_time = 0.0
            total_wait_time = 0.0

            for j in range(0, self.input.repeats):
                self.input.NN = i
                simulation = Simulation(self.input)
                simulation.run()

                temp_total_cycle_count = 0.0
                temp_probability_of_rts_success = 0.0
                temp_probability_of_rts_collision = 0.0
                temp_probability_of_channel_free = 0.0
                temp_probability_of_channel_busy = 0.0
                temp_failure_count = 0.0
                temp_success_count = 0.0
                temp_wait_count = 0.0
                temp_cycle_time = 0.0
                temp_cycle_time2 = 0.0
                temp_cycle_time3 = 0.0
                temp_idle_time = 0.0
                temp_backoff_time = 0.0
                temp_rts_time = 0.0
                temp_cts_time = 0.0
                temp_out_time = 0.0
                temp_data_time = 0.0
                temp_refrain_time = 0.0
                temp_wait_time = 0.0
                temp_time_between_tx = 0.0
                temp_not_tx_rx_time = 0.0
                temp_channel_busy_time = 0.0

                simulation_time += simulation.time
                for node in simulation.nodes:
                    temp_total_cycle_count += node.statistics.total_cycle_count
                    temp_probability_of_rts_success += node.statistics.probability_of_rts_success
                    temp_probability_of_rts_collision += node.statistics.probability_of_rts_collision
                    temp_probability_of_channel_free += node.statistics.probability_of_channel_free
                    temp_probability_of_channel_busy += node.statistics.probability_of_channel_busy
                    temp_failure_count += node.statistics.probability_of_failure
                    temp_success_count += node.statistics.probability_of_success
                    temp_wait_count += node.statistics.probability_of_wait
                    temp_cycle_time += node.statistics.cycle_time
                    temp_cycle_time2 += node.statistics.cycle_time2
                    temp_cycle_time3 += node.statistics.cycle_time2 * node.cycle_count
                    temp_idle_time += node.statistics.idle_time
                    temp_backoff_time += node.statistics.backoff_time
                    temp_rts_time += node.statistics.rts_time
                    temp_cts_time += node.statistics.cts_time
                    temp_out_time += node.statistics.out_time
                    temp_data_time += node.statistics.data_time
                    temp_refrain_time += node.statistics.refrain_time
                    temp_wait_time += node.statistics.wait_time
                    temp_time_between_tx += node.idle_series_statistics.time
                    temp_not_tx_rx_time += node.statistics.not_tx_rx_time
                    temp_channel_busy_time += node.statistics.channel_busy_time

                    total_idle_time += node.statistics.total_idle_time
                    total_success_time += node.statistics.total_success_cycle_time
                    total_failure_time += node.statistics.total_failure_cycle_time
                    total_rts_time += node.statistics.total_rts_time
                    total_data_time += node.statistics.total_data_time
                    total_wait_time += node.statistics.total_wait_time

                total_cycle_count += temp_total_cycle_count / len(simulation.nodes)
                probability_of_rts_success += temp_probability_of_rts_success / len(simulation.nodes)
                probability_of_rts_collision += temp_probability_of_rts_collision / len(simulation.nodes)
                probability_of_channel_free += temp_probability_of_channel_free / len(simulation.nodes)
                probability_of_channel_busy += temp_probability_of_channel_busy / len(simulation.nodes)
                probability_of_failure += temp_failure_count / len(simulation.nodes)
                probability_of_success += temp_success_count / len(simulation.nodes)
                probability_of_wait += temp_wait_count / len(simulation.nodes)
                cycle_time += temp_cycle_time / len(simulation.nodes)
                cycle_time2 += temp_cycle_time2 / len(simulation.nodes)
                cycle_time3 += temp_cycle_time3 / len(simulation.nodes)
                idle_time += temp_idle_time / len(simulation.nodes)
                backoff_time += temp_backoff_time / len(simulation.nodes)
                rts_time += temp_rts_time / len(simulation.nodes)
                cts_time += temp_cts_time / len(simulation.nodes)
                out_time += temp_out_time / len(simulation.nodes)
                data_time += temp_data_time / len(simulation.nodes)
                refrain_time += temp_refrain_time / len(simulation.nodes)
                wait_time += temp_wait_time / len(simulation.nodes)
                time_between_tx += temp_time_between_tx / len(simulation.nodes)
                not_tx_rx_time += temp_not_tx_rx_time / len(simulation.nodes)
                channel_busy_time += temp_channel_busy_time / len(simulation.nodes)

                total_success_time /= len(simulation.nodes)
                total_failure_time /= len(simulation.nodes)

                total_idle_time /= len(simulation.nodes)
                total_backoff_time /= len(simulation.nodes)
                total_rts_time /= len(simulation.nodes)
                total_cts_time /= len(simulation.nodes)
                total_out_time /= len(simulation.nodes)
                total_data_time /= len(simulation.nodes)
                total_wait_time /= len(simulation.nodes)

            total_cycle_count = total_cycle_count / self.input.repeats
            probability_of_rts_success = probability_of_rts_success / self.input.repeats
            probability_of_rts_collision = probability_of_rts_collision / self.input.repeats
            probability_of_channel_free = probability_of_channel_free / self.input.repeats
            probability_of_channel_busy = probability_of_channel_busy / self.input.repeats
            probability_of_failure = probability_of_failure / self.input.repeats
            probability_of_success = probability_of_success / self.input.repeats
            probability_of_wait = probability_of_wait / self.input.repeats
            cycle_time = cycle_time / self.input.repeats
            cycle_time2 = cycle_time2 / self.input.repeats
            cycle_time3 = (cycle_time3 / self.input.repeats) / total_cycle_count

            idle_time = idle_time / self.input.repeats
            backoff_time = backoff_time / self.input.repeats
            rts_time = rts_time / self.input.repeats
            cts_time = cts_time / self.input.repeats
            out_time = out_time / self.input.repeats
            data_time = data_time / self.input.repeats
            refrain_time = refrain_time / self.input.repeats
            wait_time = wait_time / self.input.repeats
            channel_busy_time = channel_busy_time / self.input.repeats

            simulation_time /= self.input.repeats

            total_success_time /= self.input.repeats
            total_failure_time /= self.input.repeats

            total_idle_time /= self.input.repeats
            total_backoff_time /= self.input.repeats
            total_rts_time /= self.input.repeats
            total_cts_time /= self.input.repeats
            total_out_time /= self.input.repeats
            total_data_time /= self.input.repeats
            total_refrain_time /= self.input.repeats
            total_wait_time /= self.input.repeats

            self.statistics[i] = [
                i,
                self.input.p_a,
                probability_of_rts_success,
                probability_of_rts_collision,
                probability_of_success,
                probability_of_failure,
                probability_of_channel_free,
                probability_of_channel_busy,
                probability_of_wait,
                self.input.time_multiplier * idle_time,
                self.input.time_multiplier * backoff_time,
                self.input.time_multiplier * rts_time,
                self.input.time_multiplier * cts_time,
                self.input.time_multiplier * out_time,
                self.input.time_multiplier * data_time,
                self.input.time_multiplier * refrain_time,
                self.input.time_multiplier * wait_time,
                pow(10,9) * cycle_time,
                0 if cycle_time2 == 0 else (rts_time) / cycle_time2,
                data_time / cycle_time2,
            ]

            self.detailed_statistics[i] = [
                i,
                total_cycle_count,
                probability_of_failure,
                probability_of_success,

                pow(10,9) * cycle_time,
                self.input.time_multiplier * cycle_time2,
                self.input.time_multiplier * cycle_time3,
                self.input.time_multiplier * rts_time,
                self.input.time_multiplier * data_time,
                self.input.time_multiplier * wait_time,
                self.input.time_multiplier * channel_busy_time,

                (rts_time) / cycle_time,
                0 if cycle_time2 == 0 else (rts_time) / cycle_time2,
                (rts_time) / cycle_time3,
                total_rts_time / simulation_time,

                data_time / cycle_time,
                data_time / cycle_time2,
                self.input.Tdata * probability_of_success / cycle_time3,
                total_data_time / simulation_time,

                channel_busy_time / cycle_time,
                channel_busy_time / cycle_time2,

            ]

            t2 = time.time()
            print("     Executed in %s seconds" % (t2 - t1))

        end_time = time.time()
        print("Executed in %s seconds" % (end_time - start_time))

    def output(self, input, file_name, statistics_type):
        if not StatisticsType.__contains__(statistics_type):
            raise ValueError("Please provide valid statistics type: %s", StatisticsType.value )

        statistics_description = None
        statistics = None

        if statistics_type == StatisticsType.statistics:
            statistics_description = self.statistics_description
            statistics = self.statistics
        else:
            statistics_description = self.detailed_statistics_description
            statistics = self.detailed_statistics

        filename = input.generate_output_filename(file_name + "_" + statistics_type._name_)
        kwargs = {'newline': ''}
        mode = 'w'

        print("Saved results to " + filename)

        with open(filename, mode, **kwargs) as fp:
            writer = csv.writer(fp, delimiter=';')

            description = []
            for x in statistics_description.values():
                description.append(x)

            print(description)
            writer.writerow(description)

            for keys, values in statistics.items():
                print(values)
                writer.writerow(values)

        print()

    def debug(self):
        for i in self.detailed_statistics.keys():
            print("Nodes = ", i)
            for index, description in self.detailed_statistics:
                print("     ", description, "=", self.statistics[i][index])

