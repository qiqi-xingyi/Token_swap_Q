# -*- coding: utf-8 -*-
# time: 2023/10/6 22:47
# file: graph_.py
# author: Felix_Zhang
# email: yuqizhang247@gmail.com

from graph.get_graph import circuit_to_rustworkx_graph, quantum_ciriuit



if __name__ == '__main__':

    circuit = quantum_ciriuit()

    graph = circuit_to_rustworkx_graph(circuit)







