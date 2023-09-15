# from qiskit import *
# from qiskit.quantum_info import Operator
# from qiskit.compiler import transpile
# from qiskit.compiler import transpiler

# from qiskit import QuantumCircuit, execute, Aer
# import numpy as np
# from numpy import pi
# from qiskit import Aer, transpile
# from qiskit.tools.visualization import plot_histogram, plot_state_city
# from qiskit.providers.aer.library import save_unitary
# import qiskit.quantum_info as qi

# from numpy import pi
# import numpy as np
# from collections.abc import Iterable
# def toQiskitcirc(circuit,qubits,show=False):
#     qubits = list(qubits)
#     qc = QuantumCircuit(len(qubits))
#     for c in circuit:
#     #     print(c)
#         if c[0] == 'CZ':
#             idx1, idx2 = qubits.index(c[1][0]), qubits.index(c[1][1])
#             qc.cz(idx1, idx2)
# #         elif 'rfUnitary' in c[0]:
# #             idx = qubits.index(c[1])
# #             qc.ry(c[0][1],idx)
#         elif 'Rz' in c[0]:
#             idx = qubits.index(c[1])
#             qc.rz(c[0][1],idx)
#         elif 'Ry' in c[0]:
#             idx = qubits.index(c[1])
#             qc.ry(c[0][1],idx)
#         elif 'Rx' in c[0]:
#             idx = qubits.index(c[1])
#             qc.rx(c[0][1],idx)
#         elif 'X/2' == c[0]:
#             idx = qubits.index(c[1])
#             qc.rx(np.pi/2,idx)
#         elif 'X' == c[0]:
#             idx = qubits.index(c[1])
#             qc.x(idx)
#         elif '-X/2' == c[0]:
#             idx = qubits.index(c[1])
#             qc.rx(-np.pi/2,idx)
#         elif 'H' == c[0]:
#             idx = qubits.index(c[1])
#             qc.h(idx)
#         elif 'Barrier' == c[0]:
#             qc.barrier()
#         elif 'delay' == c[0][0]:
#             idx = qubits.index(c[1])
#             qc.delay(c[0][1],idx)
#         elif 'Id' == c[0]:
#             idx = qubits.index(c[1])
#             qc.i(idx)
#         else:
#             pass
#     if show:
#         qc.draw(output='mpl')
#     return qc

# def getCounts(qc,shots=30000):
#     qc.measure_all()
#     backend = Aer.get_backend('qasm_simulator')
#     job = execute(qc,backend,shots=shots,basis_gates=None)
#     result = job.result()
#     counts = result.get_counts()
#     return counts
        