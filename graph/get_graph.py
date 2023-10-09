# -*- coding: utf-8 -*-
# time: 2023/10/6 22:51
# file: get_graph.py
# author: Felix_Zhang
# email: yuqizhang247@gmail.com

from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
import rustworkx as rx
import matplotlib.pyplot as plt
from rustworkx.visualization import mpl_draw
from rustworkx.visualization import graphviz_draw


# taking graph from LC and AC

'''
LC = (Q , C)
In this , Q means qubit. C means CNOT.
g means time.
Such as,
Q = {q0 , q1  , q2 , q3}
C = {g0 = (q2,q0) , g1 = (q3,q2) , g2 = (q0,q3) , ...}
'''

def quantum_ciriuit():
    circuit = QuantumCircuit(4)

    circuit.cx(0, 1)
    circuit.cx(1, 2)
    circuit.cx(2, 3)
    circuit.cx(3, 1)
    circuit.cx(0, 2)
    circuit.cx(3, 2)
    circuit.cx(2, 0)
    circuit.cx(3, 0)
    circuit.cx(2, 1)

    print(circuit)

    return circuit


def circuit_to_rustworkx_graph(circuit: QuantumCircuit):
    # create a PyGraph
    graph = rx.PyGraph()

    # add qubit for Q(as the node of graph)
    qubit_indices = {qubit: graph.add_node(f"q{circuit.qubits.index(qubit)}") for qubit in circuit.qubits}

    # add CNOT gate as edge for C
    for gate, qubits, _ in circuit.data:
        if gate.name == "cx":
            control_index = qubit_indices[qubits[0]]
            target_index = qubit_indices[qubits[1]]
            # add edge
            # if not graph.has_edge(control_index, target_index):
            graph.add_edge(control_index, target_index, None)

    # print node
    print("Nodes:", graph.nodes())

    # print edge
    print("Edges:", graph.edge_list())

    mpl_draw(graph)
    plt.show()

    return graph