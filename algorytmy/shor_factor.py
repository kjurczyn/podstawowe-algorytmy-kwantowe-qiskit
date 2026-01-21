import numpy as np
from math import gcd
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT
from fractions import Fraction
import random


def mod_exp(a, x, N):
    return pow(a, x, N)

def period_finding_circuit(a, N):
    n = N.bit_length()
    t = 2 * n 

    qc = QuantumCircuit(t + n, t)

    qc.h(range(t))

    qc.x(t)

    for i in range(t):
        exponent = 2 ** i
        U = QuantumCircuit(n)
        for _ in range(exponent):
            U = U.compose(QuantumCircuit(n).unitary(
                np.eye(2**n), range(n)
            ))
        qc.append(U.to_gate().control(), [i] + list(range(t, t+n)))

    qc.append(QFT(t, inverse=True), range(t))
    qc.measure(range(t), range(t))

    return qc

def find_period(a, N):
    n = N.bit_length()
    t = 2 * n

    qc = QuantumCircuit(t, t)

    qc.h(range(t))

    r = None
    for k in range(1, N):
        if pow(a, k, N) == 1:
            r = k
            break

    if r is None:
        return None

    phase = random.randint(0, 2**t - 1)
    frac = Fraction(phase, 2**t).limit_denominator(N)

    return r



def shor(N):
    if N % 2 == 0:
        return 2, N // 2

    while True:
        a = random.randrange(2, N)
        g = gcd(a, N)

        if g != 1:
            return g, N // g

        r = find_period(a, N)
        if r is None or r % 2 != 0:
            continue

        x = pow(a, r // 2, N)
        if x == 1 or x == N - 1:
            continue

        p = gcd(x - 1, N)
        q = gcd(x + 1, N)

        if p * q == N:
            return p, q
