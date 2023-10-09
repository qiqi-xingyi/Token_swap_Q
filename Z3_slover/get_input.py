# -*- coding: utf-8 -*-
# time: 2023/10/7 17:28
# file: get_input.py
# author: Felix_Zhang
# email: yuqizhang247@gmail.com

def get_input(circ_str: str):

    gates = list()  # which qubit(s) each gate acts on
    gate_spec = list()  # type of each gate
    qubit_num = 0

    for qasmline in circ_str.splitlines():
        words = qasmline.split()
        if not isinstance(words, list): continue  # empty lines
        if len(words) == 0: continue

        grammar = len(words)
        # grammer=2 -> single-qubit_gate_name one_qubit
        #              |two-qubit_gate_name one_qubit,one_qubit
        # grammer=3 ->  two-qubit_gate_name one_qubit, one_qubit
        # grammer=1 or >3 incorrect, raise an error

        if words[0] in ["OPENQASM", "include", "creg", "measure", "//"]:
            continue

        if words[0] == 'qreg':
            qubit_num = int(words[1][2:-2])
            continue

        if words[0] == 'cx' or words[0] == 'zz':
            if grammar == 3:
                try:
                    qubit0 = int(words[1][2:-2])
                    qubit1 = int(words[2][2:-2])
                except:
                    raise ValueError(f"{qasmline} invalid two-qubit gate.")

            elif grammar == 2:
                qubits = words[1].split(',')
                try:
                    qubit0 = int(qubits[0][2:-1])
                    qubit1 = int(qubits[1][2:-2])
                except:
                    raise ValueError(f"{qasmline} invalid two-qubit gate.")

            else:
                raise ValueError(f"{qasmline}: invalid two-qubit gate.")

            gates.append((qubit0, qubit1))
            gate_spec.append(words[0])

        elif grammar == 2:  # not two-qubit gate, and has two words
            try:
                qubit = int(words[1][2:-2])
            except:
                raise ValueError(f"{qasmline} invalid single-qubit gate.")
            gates.append((qubit,))
            gate_spec.append(words[0])

        else:
            raise ValueError(f"{qasmline} invalid gate.")

    if qubit_num == 0:
        raise ValueError("Qubit number is not specified.")
    return [qubit_num, tuple(gates), tuple(gate_spec)]