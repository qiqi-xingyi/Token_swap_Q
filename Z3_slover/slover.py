# -*- coding: utf-8 -*-
# time: 2023/10/9 21:51
# file: slover.py
# author: Felix_Zhang
# email: yuqizhang247@gmail.com

from z3 import *

from Z3_slover.get_input import get_input
from Z3_slover.get_output import get_output
from Z3_slover.device import get_device

import math
import datetime
import pkgutil

def collect_collision(list_gate_qubits):
    # find collision with some gates
    gate_list = list()

    for gate in range(len(list_gate_qubits)):
        for double_gate in range(gate + 1, len(list_gate_qubits)):

            if list_gate_qubits[gate][0] == list_gate_qubits[double_gate][0]:

                gate_list.append((gate, double_gate))

            if len(list_gate_qubits[double_gate]) == 2:

                if list_gate_qubits[gate][0] == list_gate_qubits[double_gate][1]:

                    gate_list.append((gate, double_gate))

            if len(list_gate_qubits[gate]) == 2:

                if list_gate_qubits[gate][1] == list_gate_qubits[double_gate][0]:

                    gate_list.append((gate, double_gate))

                if len(list_gate_qubits[double_gate]) == 2:

                    if list_gate_qubits[gate][1] == list_gate_qubits[double_gate][1]:

                        gate_list.append((gate, double_gate))


    return tuple(gate_list)

def dependency_extracting(gate_list, count_program_qubit: int):
    # find the dependency of gate

    """
     last_gate_list records the latest gate that acts on each qubit.
     When we sweep through all the gates, this list is updated and the
     dependencies induced by the update is noted.

    :param gate_list: a list of gate
    :param count_program_qubit: the number of logical qubits
    :return: a list of dependency of gates
    """

    dependency_gate_list = []
    last_gate_list = [-1 for i in range(count_program_qubit)]

    for i, qubits in enumerate(gate_list):

        if last_gate_list[qubits[0]] >= 0:
            dependency_gate_list.append((last_gate_list[qubits[0]], i))
        last_gate_list[qubits[0]] = i

        if len(qubits) == 2:
            if last_gate_list[qubits[1]] >= 0:
                dependency_gate_list.append((last_gate_list[qubits[1]], i))
            last_gate_list[qubits[1]] = i

    return tuple(dependency_gate_list)


class token_swapping:

    def __init__(self):

        # These values should be updated in setdevice
        self.device = None
        self.count_physical_qubit = 0
        self.list_qubit_edge = []
        self.swap_duration = 0

        # These values should be updated in setprogram
        self.list_gate_qubits = []
        self.count_program_qubit = 0
        self.list_gate_name = []

        # bound_depth is a hyperparameter
        self.bound_depth = 0
        self.inpput_dependency = False
        self.list_gate_dependency = []

    def setdevice(self, device: get_device):
        #get the device information from the json film
        self.device = device
        self.count_physical_qubit = device.count_physical_qubit
        self.list_qubit_edge = device.list_qubit_edge
        self.swap_duration = device.swap_duration
        self.swap_duration = 1

    def setprogram(self, program, input_mode: str = None):
        # deal with the logical quantum circuit

        # f = pkgutil.get_data(__name__, "benchmarks/" + program + ".qasm")
        # program = get_input(f.decode("utf-8"))
        # self.count_program_qubit = program[0]
        # self.list_gate_qubits = program[1]
        # self.list_gate_name = program[2]
        program = get_input(program)
        self.count_program_qubit = program[0]
        self.list_gate_qubits = program[1]
        self.list_gate_name = program[2]


        self.bound_depth = 1

    def setdependency(self, dependency: list):
        # set the dependency flag

        self.list_gate_dependency = dependency
        self.inpput_dependency = True

    ###################################### slover ##########################################

    def solve(self, output_mode: str = None, output_file_name: str = None):
        # set the problem as a SMT problem , put it in Z3-slover,
        # get the result

        # objective_name = self.objective_name

        device = self.device
        list_gate_qubits = self.list_gate_qubits
        count_program_qubit = self.count_program_qubit
        list_gate_name = self.list_gate_name
        count_physical_qubit = self.count_physical_qubit
        list_qubit_edge = self.list_qubit_edge
        swap_duration = self.swap_duration
        bound_depth = self.bound_depth

        # pre-processing

        count_qubit_edge = len(list_qubit_edge)
        count_gate = len(list_gate_qubits)

        list_gate_two = list()
        list_gate_single = list()
        for l in range(count_gate):
            if len(list_gate_qubits[l]) == 1:
                list_gate_single.append(l)
            else:
                list_gate_two.append(l)



        list_adjacent_qubit = list()

        list_span_edge = list()

        for n in range(count_physical_qubit):
            list_adjacent_qubit.append(list())
            list_span_edge.append(list())

        for k in range(count_qubit_edge):
            list_adjacent_qubit[list_qubit_edge[k][0]].append(list_qubit_edge[k][1])

            list_adjacent_qubit[list_qubit_edge[k][1]].append(list_qubit_edge[k][0])

            list_span_edge[list_qubit_edge[k][0]].append(k)

            list_span_edge[list_qubit_edge[k][1]].append(k)

        # collect overlap edge
        if_overlap_edge = [[0] * count_qubit_edge for k in range(count_qubit_edge)]
        list_overlap_edge = list()

        list_count_overlap_edge = list() # a list of lengths of overlap edge

        for k in range(count_qubit_edge):
            list_overlap_edge.append(list())



        for k in range(count_qubit_edge):
            for kk in range(k + 1, count_qubit_edge):
                if ((list_qubit_edge[k][0] == list_qubit_edge[kk][0]
                     or list_qubit_edge[k][0] == list_qubit_edge[kk][1])
                        or (list_qubit_edge[k][1] == list_qubit_edge[kk][0]
                            or list_qubit_edge[k][1] == list_qubit_edge[kk][1])):
                    list_overlap_edge[k].append(kk)
                    list_overlap_edge[kk].append(k)
                    if_overlap_edge[kk][k] = 1
                    if_overlap_edge[k][kk] = 1


        for k in range(count_qubit_edge):
            list_count_overlap_edge.append(len(list_overlap_edge[k]))


        if not self.inpput_dependency:
            list_gate_dependency = collect_collision(list_gate_qubits)
        else:
            list_gate_dependency = self.list_gate_dependency


        # takes two physical qubit and returns the index of the edge between them

        map_edge_index = [[0] * count_physical_qubit] * count_physical_qubit

        for k in range(count_qubit_edge):
            map_edge_index[list_qubit_edge[k][0]][list_qubit_edge[k][1]] = k
            map_edge_index[list_qubit_edge[k][1]][list_qubit_edge[k][0]] = k

        start_time = datetime.datetime.now()
        not_solved = True
        count_swap = 0

        while not_solved:

            print("{} time solving".format(bound_depth))



            ######### variable setting #########

            # at cycle t, logical qubit q is mapped to pi[q][t]
            pi = [[Int("map_q{}_t{}".format(i, j)) for j in range(bound_depth)] for i in range(count_program_qubit)]

            # time coordinate for gate l is time[l]
            time = IntVector('time', count_gate)

            # space coordinate for gate l is space[l]
            space = IntVector('space', count_gate)

            # if at cycle t, a SWAP finishing on edge k, then sigma[k][t]=1
            sigma = [[Bool("ifswap_e{}_t{}".format(i, j))
                      for j in range(bound_depth)] for i in range(count_qubit_edge)]

            # for depth optimization
            depth = Int('depth')

            # for swap number optimization
            count_swap = Int('num_swap')

            ############## build a slover ##############

            SMT_slover = Optimize()

            ############ set the constraint ############



            for t in range(bound_depth):

                for m in range(count_program_qubit):

                    SMT_slover.add(pi[m][t] >= 0, pi[m][t] < count_physical_qubit)

                    for mm in range(m):

                        SMT_slover.add(pi[m][t] != pi[mm][t])

            for l in range(count_gate):
                SMT_slover.add(time[l] >= 0, time[l] < bound_depth)
                if l in list_gate_single:
                    SMT_slover.add(space[l] >= 0, space[l] < count_physical_qubit)
                    for t in range(bound_depth):
                        SMT_slover.add(Implies(time[l] == t,pi[list_gate_qubits[l][0]][t] == space[l]))

                elif l in list_gate_two:
                    SMT_slover.add(space[l] >= 0, space[l] < count_qubit_edge)
                    for k in range(count_qubit_edge):
                        for t in range(bound_depth):
                            SMT_slover.add(Implies(And(time[l] == t, space[l] == k),
                                             Or(And(list_qubit_edge[k][0] == \
                                                    pi[list_gate_qubits[l][0]][t],
                                                    list_qubit_edge[k][1] == \
                                                    pi[list_gate_qubits[l][1]][t]),
                                                And(list_qubit_edge[k][1] == \
                                                    pi[list_gate_qubits[l][0]][t],
                                                    list_qubit_edge[k][0] == \
                                                    pi[list_gate_qubits[l][1]][t]))))


            for d in list_gate_dependency:

                    SMT_slover.add(time[d[0]] < time[d[1]])

            for t in range(min(swap_duration - 1, bound_depth)):
                for k in range(count_qubit_edge):
                    SMT_slover.add(sigma[k][t] == False)

            for t in range(swap_duration - 1, bound_depth):
                for k in range(count_qubit_edge):
                    for tt in range(t - swap_duration + 1, t):
                        SMT_slover.add(Implies(sigma[k][t] == True,
                                         sigma[k][tt] == False))
                    for tt in range(t - swap_duration + 1, t + 1):
                        for kk in list_overlap_edge[k]:
                            SMT_slover.add(Implies(sigma[k][t] == True,
                                             sigma[kk][tt] == False))

            # mapping Pi
            for t in range(bound_depth - 1):
                for n in range(count_physical_qubit):
                    for m in range(count_program_qubit):
                        SMT_slover.add(
                            Implies(And(sum([If(sigma[k][t], 1, 0)
                                             for k in list_span_edge[n]]) == 0,
                                        pi[m][t] == n), pi[m][t + 1] == n))

            for t in range(bound_depth - 1):
                for k in range(count_qubit_edge):
                    for m in range(count_program_qubit):
                        SMT_slover.add(Implies(And(sigma[k][t] == True,
                                                   pi[m][t] == list_qubit_edge[k][0]),
                                               pi[m][t + 1] == list_qubit_edge[k][1]))
                        SMT_slover.add(Implies(And(sigma[k][t] == True,
                                                   pi[m][t] == list_qubit_edge[k][1]),
                                               pi[m][t + 1] == list_qubit_edge[k][0]))

            SMT_slover.add(count_swap == sum([If(sigma[k][t], 1, 0)
                                              for k in range(count_qubit_edge)
                                              for t in range(bound_depth)]))

            # for depth optimization
            for l in range(count_gate):
                SMT_slover.add(depth >= time[l] + 1)

            SMT_slover.minimize(count_swap)

            satisfiable = SMT_slover.check()

            if satisfiable == sat:
                not_solved = False
            else:
                bound_depth += 1


###################################### get result ##########################################

        print("################ Result ##################")

        print(f"Compilation time = {datetime.datetime.now() - start_time}.")

        model = SMT_slover.model()

        result_time = []
        result_depth = model[depth].as_long()

        for l in range(count_gate):
            result_time.append(model[time[l]].as_long())


        list_result_swap = []
        # get the swap in result
        for k in range(count_qubit_edge):
            for t in range(result_depth):
                if model[sigma[k][t]]:
                    list_result_swap.append((k, t))
                    print(f"Time = {t} || SWAP on physical edge ({list_qubit_edge[k][0]}," + f"{list_qubit_edge[k][1]})")

        for l in range(count_gate):
            if len(list_gate_qubits[l]) == 1:
                qq = list_gate_qubits[l][0]
                tt = result_time[l]
                print(f"* Time = {tt} || g{l}: {list_gate_name[l]} {qq} , qubit: " + f"{model[pi[qq][tt]].as_long()}")


            else:
                qq = list_gate_qubits[l][0]
                qqq = list_gate_qubits[l][1]
                tt = result_time[l]
                print(f"# Gate {l}: {list_gate_name[l]} ({qq}, {qqq}) on qubits " \
                      + f"[{model[pi[qq][tt]].as_long()}, " \
                      + f"{model[pi[qqq][tt]].as_long()}] || Time = {tt}")

        objective_value = 0

        objective_value = len(list_result_swap)
        print(f"Find solution when k(SWAP count) = {objective_value}.")

        list_scheduled_gate_qubits = [[] for i in range(result_depth)]
        list_scheduled_gate_name = [[] for i in range(result_depth)]
        result_depth = 0


        for l in range(count_gate):
            t = result_time[l]

            if result_depth < t + 1:
                result_depth = t + 1

            list_scheduled_gate_name[t].append(list_gate_name[l])

            if l in list_gate_single:
                q = model[space[l]].as_long()
                list_scheduled_gate_qubits[t].append((q,))

            elif l in list_gate_two:
                [q0, q1] = list_gate_qubits[l]

                # tmp_t = t

                tmp_t = model[time[l]].as_long()
                q0 = model[pi[q0][tmp_t]].as_long()
                q1 = model[pi[q1][tmp_t]].as_long()
                list_scheduled_gate_qubits[t].append((q0, q1))

            else:
                raise ValueError("Expect single-qubit or two-qubit gate.")

        final_mapping = []

        for m in range(count_program_qubit):

            tmp_depth = result_depth - 1

            tmp_depth = model[depth].as_long() - 1
            final_mapping.append(model[pi[m][tmp_depth]].as_long())


        for (k, t) in list_result_swap:

            q0 = list_qubit_edge[k][0]
            q1 = list_qubit_edge[k][1]

            list_scheduled_gate_qubits[t].append((q0, q1))
            list_scheduled_gate_name[t].append("SWAP")


