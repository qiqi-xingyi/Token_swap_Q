# -*- coding: utf-8 -*-
# time: 2023/10/7 17:38
# file: device.py
# author: Felix_Zhang
# email: yuqizhang247@gmail.com

import json
import pkgutil

####################################
# get device from json

class get_device:

    def __init__(self, name: str, nqubits: int = None, connection: list = None,
                 swap_duration: int = None, fmeas: list = None,
                 fsingle: list = None, ftwo: list = None):


        # typechecking for inputs
        if not isinstance(name, str):
            raise TypeError("name should be a string.")
        if nqubits is not None:
            if not isinstance(nqubits, int):
                raise TypeError("nqubits should be an integer.")
        if swap_duration is not None:
            if not isinstance(swap_duration, int):
                raise TypeError("swap_duration should be an integer.")

        if connection is not None:
            if not isinstance(connection, (list, tuple)):
                raise TypeError("connection should be a list or tuple.")
            else:
                for edge in connection:
                    if not isinstance(edge, (list, tuple)):
                        raise TypeError(f"{edge} is not a list or tuple.")
                    elif len(edge) != 2:
                        raise TypeError(f"{edge} does not connect two qubits.")
                    if not isinstance(edge[0], int):
                        raise TypeError(f"{edge[0]} is not an integer.")
                    if not isinstance(edge[1], int):
                        raise TypeError(f"{edge[1]} is not an integer.")

        if fmeas is not None:
            if not isinstance(fmeas, (list, tuple)):
                raise TypeError("fmeas should be a list or tuple.")
            else:
                for fmeas_i in fmeas:
                    if not isinstance(fmeas_i, (int, float)):
                        raise TypeError(f"{fmeas_i} is not a number.")
        if fsingle is not None:
            if not isinstance(fsingle, (list, tuple)):
                raise TypeError("fsingle should be a list or tuple.")
            else:
                for fsingle_i in fsingle:
                    if not isinstance(fsingle_i, (int, float)):
                        raise TypeError(f"{fsingle_i} is not a number.")
        if ftwo is not None:
            if not isinstance(ftwo, (list, tuple)):
                raise TypeError("ftwo should be a list or tuple.")
            else:
                for ftwo_i in ftwo:
                    if not isinstance(ftwo_i, (int, float)):
                        raise TypeError(f"{ftwo_i} is not a number.")
                    


        if name.startswith("default_"):
            # use an existing device
            f = pkgutil.get_data(__name__ ,"devices/" + name + ".json")

            data = json.loads(f)

            self.name = data["name"]

            self.count_physical_qubit = data["count_physical_qubit"]
            self.list_qubit_edge = tuple(tuple(edge)for edge in data["list_qubit_edge"])
            self.swap_duration = data["swap_duration"]

            if "list_fidelity_measure" in data:
                self.list_fidelity_measure = \
                    tuple(data["list_fidelity_measure"])
            if "list_fidelity_single" in data:
                self.list_fidelity_single = tuple(data["list_fidelity_single"])
            if "list_fidelity_two" in data:
                self.list_fidelity_two = tuple(data["list_fidelity_two"])
        else:
            self.name = name

        # set parameters from inputs with value checking
        if nqubits is not None:
            self.count_physical_qubit = nqubits
        if "count_physical_qubit" not in self.__dict__:
            raise AttributeError("No physical qubit count specified.")

        if connection is not None:
            for edge in connection:
                if edge[0] < 0 or edge[0] >= self.count_physical_qubit:
                    raise ValueError((f"{edge[0]} is outside of range "
                                      f"[0, {self.count_physical_qubit})."))
                if edge[1] < 0 or edge[1] >= self.count_physical_qubit:
                    raise ValueError((f"{edge[1]} is outside of range "
                                      f"[0, {self.count_physical_qubit})."))
            self.list_qubit_edge = tuple(tuple(edge) for edge in connection)
        if "list_qubit_edge" not in self.__dict__:
            raise AttributeError("No edge set is specified.")

        if swap_duration is not None:
            self.swap_duration = swap_duration
        else:
            self.swap_duration = 3

        if fmeas is not None:
            if len(fmeas) != self.count_physical_qubit:
                raise ValueError(("fmeas should have "
                                  f"{self.count_physical_qubit} data."))
            self.list_fidelity_measure = tuple(fmeas)
        if "list_fidelity_measure" not in self.__dict__:
            self.list_fidelity_measure = \
                tuple(1 for _ in range(self.count_physical_qubit))

        if fsingle is not None:
            if len(fsingle) != self.count_physical_qubit:
                raise ValueError(("fsingle should have "
                                  f"{self.count_physical_qubit} data."))
            self.list_fidelity_single = tuple(fsingle)
        if "list_fidelity_single" not in self.__dict__:
            self.list_fidelity_single = \
                tuple(1 for _ in range(self.count_physical_qubit))

        if ftwo is not None:
            if len(ftwo) != len(self.list_qubit_edge):
                raise ValueError(("ftwo should have "
                                  f"{len(self.list_qubit_edge)} data."))
            self.list_fidelity_two = tuple(ftwo)
        if "list_fidelity_two" not in self.__dict__:
            self.list_fidelity_two = \
                tuple(1 for _ in range(len(self.list_qubit_edge)))