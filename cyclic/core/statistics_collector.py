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
            rts_time = 0.0
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
                temp_rts_time = 0.0

                for node in simulation.nodes:
                    temp_total_cycle_count += node.statistics.total_cycle_count
                    temp_failure_count += node.statistics.failure_count
                    temp_success_count += node.statistics.success_count
                    temp_cycle_time += node.statistics.cycle_time
                    temp_rts_time += node.statistics.rts_time

                total_cycle_count += temp_total_cycle_count / len(simulation.nodes)
                failure_count += temp_failure_count / len(simulation.nodes)
                success_count += temp_success_count / len(simulation.nodes)
                cycle_time += temp_cycle_time / len(simulation.nodes)
                rts_time += temp_rts_time / len(simulation.nodes)

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
                cycle_time,
                rts_time,
                received_rts,
                blocked_rts,
                not_blocked_rts,
                ignored_rts,
                blocking_probability_by_call
            ]

            t2 = time.time()
            print("     Executed in %s seconds" % (t2 - t1))

        end_time = time.time()
        print("Executed in %s seconds" % (end_time - start_time))