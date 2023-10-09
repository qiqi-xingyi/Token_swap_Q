# -*- coding: utf-8 -*-
# time: 2023/10/7 17:36
# file: taken_swapping_main.py
# author: Felix_Zhang
# email: yuqizhang247@gmail.com

# main of taken swapping
from Z3_slover.device import get_device
from Z3_slover.slover import token_swapping
from qiskit import QuantumCircuit
from qiskit.visualization import circuit_drawer
import matplotlib.pyplot as plt

LC = open("Z3_slover/benchmarks/quantum_circuit2.qasm", "r").read()
AG = get_device("default_2a")

if __name__ == '__main__':
    # turn QASM to qiskit circuit
    circuit = QuantumCircuit.from_qasm_str(LC)

    # draw the LC
    circuit_drawer(circuit, output="mpl")

    plt.show()

    TSWAP_solver = token_swapping()
    TSWAP_solver.setdevice(AG)
    TSWAP_solver.setprogram(LC)
    TSWAP_solver.solve()
    # assert TSWAP_solver.solve()[2] == 14