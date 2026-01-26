import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from sympy import Matrix


def solve_mod2_kernel(measurements):
    """
    Solve y · s = 0 (mod 2) for s given measurement outcomes y.
    """
    M = Matrix(measurements)
    M = M.applyfunc(lambda x: x % 2)

    nullsp = M.nullspace()
    if len(nullsp) == 0:
        return "0" * M.shape[1]

    s = nullsp[0]
    s = [int(x) % 2 for x in s]
    return "".join(map(str, s))

def simons_oracle(secret_s: str) -> QuantumCircuit:

    flag_bit = secret_s.find("1")

    n = len(secret_s)

    circ = QuantumCircuit(2 * n)

    for i in range(n):
        circ.cx(i, i + n)

    if flag_bit != -1:
        for index, bit_value in enumerate(secret_s):
            if bit_value not in ["0", "1"]:
                raise Exception("Incorrect char '" + bit_value + "' in secret string s:" + secret_s)
            if bit_value == "1":
                circ.cx(flag_bit, index + n)
    return circ
