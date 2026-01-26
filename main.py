"""
Podstawowe algorytmy kwantowe w Qiskit
- Algorytm Deutsch'a-Jozsy
- Algorytm Grovera
- Algorytm faktoryzacji Shora
- Algorytm problemu Simona
"""

import qiskit as qs
from qiskit_aer import AerSimulator
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from sympy import Matrix

# Importy z katalogu algorytmy
from algorytmy.deutch_jozsa import (
    OracleType,
    ORACLE_CONST_0,
    ORACLE_CONST_1,
    ORACLE_BALANCED,
    dj_oracle_generate,
    dj_algorithm_circuit_generate
)
from algorytmy.grover import (
    grover_oracle_generate,
    grover_algorithm_circuit_generate
)
from algorytmy.shor_factor import shor
from algorytmy.simon import solve_mod2_kernel, simons_oracle


def plot_counts(counts: dict, ax: Axes):
    """Rysuje wykres słupkowy z wynikami pomiarów"""
    ax.bar(list(counts.keys()), list(counts.values()))


backend = AerSimulator()


# =============================================================================
# ALGORYTM DEUTSCH'A-JOZSY
# =============================================================================


def run_deutsch_jozsa(n: int = 3):
    """Uruchamia algorytm Deutsch'a-Jozsy"""
    print("=" * 80)
    print("ALGORYTM DEUTSCH'A-JOZSY")
    print("=" * 80)
    print(f"Liczba kubitów: {n}")

    # Generowanie wyroczni
    dj_oracle_balanced, dj_oracle_balanced_gate = dj_oracle_generate(
        ORACLE_BALANCED, n)
    dj_oracle_const_0, dj_oracle_const_0_gate = dj_oracle_generate(
        ORACLE_CONST_0, n)
    dj_oracle_const_1, dj_oracle_const_1_gate = dj_oracle_generate(
        ORACLE_CONST_1, n)

    # Tworzenie obwodów
    dj_circuit_balanced_transpiled = qs.transpile(
        dj_algorithm_circuit_generate(dj_oracle_balanced_gate, n), backend)
    dj_circuit_const_0_transpiled = qs.transpile(
        dj_algorithm_circuit_generate(dj_oracle_const_0_gate, n), backend)
    dj_circuit_const_1_transpiled = qs.transpile(
        dj_algorithm_circuit_generate(dj_oracle_const_1_gate, n), backend)

    # Wykonanie pomiarów
    counts_balanced = backend.run(
        dj_circuit_balanced_transpiled, shots=1024).result().get_counts()
    counts_const_0 = backend.run(
        dj_circuit_const_0_transpiled, shots=1024).result().get_counts()
    counts_const_1 = backend.run(
        dj_circuit_const_1_transpiled, shots=1024).result().get_counts()

    print("\nWyniki:")
    print(f"  Wyrocznia zbalansowana: {counts_balanced}")
    print(f"  Wyrocznia stała 0: {counts_const_0}")
    print(f"  Wyrocznia stała 1: {counts_const_1}")

    # Wizualizacja
    fig, ax = plt.subplots(1, 3, figsize=(15, 4))
    ax[0].set_title('Balanced')
    ax[1].set_title('Const 0')
    ax[2].set_title('Const 1')

    for i in range(3):
        ax[i].set_ylabel('No. occurrences')
        ax[i].set_xlabel('Value')

    plot_counts(counts_balanced, ax[0])
    plot_counts(counts_const_0, ax[1])
    plot_counts(counts_const_1, ax[2])

    fig.tight_layout()

# =============================================================================
# ALGORYTM GROVERA
# =============================================================================


def run_grover(n: int = 3, marked_states: list = [1, 3]):
    """Uruchamia algorytm Grovera"""
    print("\n" + "=" * 80)
    print("ALGORYTM GROVERA")
    print("=" * 80)
    print(f"Liczba kubitów: {n}")
    print(f"Zaznaczone stany: {marked_states}")

    # Generowanie wyroczni i obwodu
    grover_oracle, grover_oracle_gate = grover_oracle_generate(
        n, marked_states)
    grover_algorithm_circuit, iterations = grover_algorithm_circuit_generate(
        grover_oracle_gate, n, len(marked_states))

    print(f"Liczba iteracji: {iterations}")

    # Wykonanie
    grover_circuit_transpiled = qs.transpile(grover_algorithm_circuit, backend)
    counts_grover = backend.run(
        grover_circuit_transpiled, shots=1024).result().get_counts()

    print(f"\nWyniki: {counts_grover}")

    # Wizualizacja
    fig, ax = plt.subplots(1, figsize=(10, 5))
    ax.set_ylabel('No. occurrences')
    ax.set_xlabel('Value')
    ax.set_title('Grover Algorithm Results')
    plot_counts(counts_grover, ax)
    fig.tight_layout()

# =============================================================================
# ALGORYTM FAKTORYZACJI SHORA
# =============================================================================


def run_shor(N: int = 15):
    """Uruchamia algorytm faktoryzacji Shora"""
    print("\n" + "=" * 80)
    print("ALGORYTM FAKTORYZACJI SHORA")
    print("=" * 80)
    print(f"Liczba do faktoryzacji: {N}")

    factors = shor(N)
    print(f"Rozkład: {N} = {factors[0]} × {factors[1]}")
    print(
        f"Weryfikacja: {factors[0]} × {factors[1]} = {factors[0] * factors[1]}")


# =============================================================================
# ALGORYTM PROBLEMU SIMONA
# =============================================================================


def run_simon(s: str = "101"):
    """Uruchamia algorytm problemu Simona"""
    print("\n" + "=" * 80)
    print("ALGORYTM PROBLEMU SIMONA")
    print("=" * 80)
    print(f"Sekretny łańcuch: {s}")

    n = len(s)

    circ = qs.QuantumCircuit(2 * n, n)
    circ.h(range(n))
    circ.compose(simons_oracle(s), inplace=True)
    circ.h(range(n))
    circ.measure(range(n), range(n))

    simulator = AerSimulator()
    shots = 10000
    task = simulator.run(circ, shots=shots)
    result = task.result()
    counts = result.get_counts()

    string_list = []
    for bitstring in counts:
        if bitstring != "0" * n:
            string_list.append([int(c) for c in bitstring])

    print(f"\nZebrane równania: {len(string_list)}")

    if string_list:
        M = Matrix(string_list)
        M = M.applyfunc(lambda x: x % 2)
        M = M.rref()[0]
        string_list = [list(map(int, row)) for row in M.tolist() if any(row)]

        result_s = solve_mod2_kernel(string_list)
        print(f"Odzyskany łańcuch: {result_s}")
        print(f"Poprawność: {'✓' if result_s == s else '✗'}")
    else:
        print("Nie zebrano żadnych równań")

    # Wizualizacja
    plt.figure(figsize=(10, 5))
    plt.bar(counts.keys(), counts.values())
    plt.xticks(rotation=90)
    plt.title("Measured bitstrings - Simon's Algorithm")
    plt.xlabel("Bitstring")
    plt.ylabel("Count")
    plt.tight_layout()

# =============================================================================
# MAIN
# =============================================================================


def main():
    """Uruchamia wszystkie algorytmy kwantowe"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "ALGORYTMY KWANTOWE W QISKIT" + " " * 31 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    # Algorytm Deutsch'a-Jozsy
    run_deutsch_jozsa(n=3)

    # Algorytm Grovera
    run_grover(n=3, marked_states=[1, 3])

    # Algorytm faktoryzacji Shora
    run_shor(N=15)

    # Algorytm problemu Simona
    run_simon(s="101")

    print("\n" + "=" * 80)
    print("ZAKOŃCZONO WSZYSTKIE ALGORYTMY")
    print("=" * 80 + "\n")

    plt.show()


if __name__ == "__main__":
    main()
