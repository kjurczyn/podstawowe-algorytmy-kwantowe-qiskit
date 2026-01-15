from typing import Callable, Iterable, NewType, Tuple
import qiskit as qs
from qiskit.circuit import Gate
import numpy as np

OracleType = NewType('OracleType', int)
ORACLE_CONST_0 = OracleType(0)
ORACLE_CONST_1 = OracleType(1)
ORACLE_BALANCED = OracleType(2)


def dj_oracle_generate(oracle_type: OracleType, n: int) -> Tuple[qs.QuantumCircuit, Gate]:
    oracle = qs.QuantumCircuit(n+1)

    if oracle_type == ORACLE_CONST_0:
        pass

    elif oracle_type == ORACLE_CONST_1:
        oracle.x(range(n))

    elif oracle_type == ORACLE_BALANCED:
        def add_cx(state: int) -> None:
            for qubit, cbit in enumerate(reversed(f"{state:0b}")):
                if cbit == '1':
                    oracle.x(qubit)

        one_states = np.random.choice(
            range(2**n), size=2**(n-1), replace=False)
        for state in one_states:
            add_cx(state)
            oracle.mcx(list(range(n)), n)
            add_cx(state)

    oracle_gate = oracle.to_gate()
    oracle_gate.name = f"Oracle"

    return oracle, oracle_gate


def dj_algorithm_circuit_generate(oracle: Gate, n: int) -> qs.QuantumCircuit:
    dj_circuit = qs.QuantumCircuit(n+1, n)
    dj_circuit.x(n)
    dj_circuit.h(range(n+1))
    dj_circuit.append(oracle, range(n+1))
    dj_circuit.h(range(n))
    dj_circuit.measure(range(n), range(n))

    return dj_circuit
