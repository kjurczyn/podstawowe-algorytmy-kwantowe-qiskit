import qiskit as qs
from qiskit.circuit import Gate
from qiskit.circuit.library import MCMTGate, ZGate
from typing import Tuple
import numpy as np


def grover_oracle_generate(n: int, marked_states: list) -> Tuple[qs.QuantumCircuit, Gate]:
    oracle = qs.QuantumCircuit(n)

    for state in marked_states:
        state_str = f"{state:0{n}b}"[::-1]
        if len(state_str) > n:
            raise ValueError()

        zeros = [zero for zero, val in enumerate(state_str) if val == '0']
        oracle.x(zeros)
        oracle.append(MCMTGate(ZGate(), n - 1, 1), range(n))
        oracle.x(zeros)

    oracle_gate = oracle.to_gate()
    oracle_gate.name = 'Oracle'

    return oracle, oracle_gate


# Generate GU_f
def grover_base_generate(oracle: Gate, n: int) -> Tuple[qs.QuantumCircuit, Gate]:
    grover_op_circuit = qs.QuantumCircuit(n)
    grover_op_circuit.append(oracle, range(n))

    # Grover diffusion operator
    grover_op_circuit.h(range(n))
    grover_op_circuit.x(range(n))
    grover_op_circuit.append(MCMTGate(ZGate(), n - 1, 1), range(n))
    grover_op_circuit.x(range(n))
    grover_op_circuit.h(range(n))

    grover_op_gate = grover_op_circuit.to_gate()
    grover_op_gate.name = 'Grover'

    return grover_op_circuit, grover_op_gate


def grover_algorithm_circuit_generate(oracle: Gate, n: int, num_states: int) -> Tuple[qs.QuantumCircuit, int]:
    grover_circuit = qs.QuantumCircuit(n, n)
    grover_circuit.h(range(n))

    grover_op_circuit, grover_op_gate = grover_base_generate(oracle, n)

    iterations = int(np.pi / 4 * np.sqrt(2**n / num_states))
    grover_circuit.append(grover_op_gate.power(iterations), range(n))

    grover_circuit.measure(range(n), range(n))

    return grover_circuit, iterations
