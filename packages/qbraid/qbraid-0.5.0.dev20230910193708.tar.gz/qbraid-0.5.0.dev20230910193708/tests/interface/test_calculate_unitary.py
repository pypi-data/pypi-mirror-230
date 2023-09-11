# Copyright (C) 2023 qBraid
#
# This file is part of the qBraid-SDK
#
# The qBraid-SDK is free software released under the GNU General Public License v3
# or later. You can redistribute and/or modify it under the terms of the GPL v3.
# See the LICENSE file in the project root or <https://www.gnu.org/licenses/gpl-3.0.html>.
#
# THERE IS NO WARRANTY for the qBraid-SDK, as per Section 15 of the GPL v3.

"""
Unit tests for the qbraid unitary interfacing

"""
from itertools import chain, combinations

import numpy as np
import pytest
from braket.circuits import Circuit, Instruction, gates
from pytket.circuit import Circuit as TKCircuit

from qbraid.exceptions import ProgramTypeError
from qbraid.interface.calculate_unitary import (
    random_unitary_matrix,
    rev_qubits_unitary,
    to_unitary,
    unitary_to_little_endian,
)
from qbraid.interface.convert_to_contiguous import convert_to_contiguous
from qbraid.interface.qbraid_pytket.tools import _gate_to_matrix_pytket


def get_subsets(nqubits):
    """Return list of all combinations up to number nqubits"""
    qubits = list(range(0, nqubits))

    def combos(x):
        return combinations(qubits, x)

    all_subsets = chain(*map(combos, range(0, len(qubits) + 1)))
    return list(all_subsets)[1:]


def calculate_expected(gates_set):
    """Calculated expected unitary"""
    if len(gates_set) == 1:
        return gates_set[0]
    if len(gates_set) == 2:
        return np.kron(gates_set[1], gates_set[0])
    return np.kron(calculate_expected(gates_set[2:]), np.kron(gates_set[1], gates_set[0]))


def generate_test_data(input_gate_set, contiguous=True):
    """Generate test data"""
    testdata = []
    gate_set = input_gate_set.copy()
    gate_set.append(gates.I)
    nqubits = len(input_gate_set)
    subsets = get_subsets(nqubits)
    for ss in subsets:
        bk_instrs = []
        np_gates = []
        for index in range(max(ss) + 1):
            idx = -1 if index not in ss else index
            BKGate = gate_set[idx]
            np_gate = BKGate().to_matrix()
            if idx != -1 or contiguous:
                bk_instrs.append((BKGate, index))
            np_gates.append(np_gate)
        u_expected = calculate_expected(np_gates)
        testdata.append((bk_instrs, u_expected))
    return testdata


def make_circuit(bk_instrs):
    """Constructs Braket circuit from list of instructions"""
    circuit = Circuit()
    for instr in bk_instrs:
        Gate, index = instr
        circuit.add_instruction(Instruction(Gate(), target=index))
    return convert_to_contiguous(circuit, expansion=True)


test_gate_set = [gates.X, gates.Y, gates.Z]
test_data_contiguous_qubits = generate_test_data(test_gate_set)
test_data_non_contiguous_qubits = generate_test_data(test_gate_set, contiguous=False)
test_data = test_data_contiguous_qubits + test_data_non_contiguous_qubits


@pytest.mark.parametrize("bk_instrs,u_expected", test_data)
def test_unitary_calc(bk_instrs, u_expected):
    """Test calculating unitary of circuits using both contiguous and
    non-contiguous qubit indexing."""
    circuit = make_circuit(bk_instrs)
    u_test = to_unitary(circuit)
    u_expected = unitary_to_little_endian(u_expected)
    assert np.allclose(u_expected, u_test)


@pytest.mark.parametrize("bk_instrs,u_expected", test_data)
def test_convert_be_to_le(bk_instrs, u_expected):
    """Test converting big-endian unitary to little-endian unitary."""
    circuit = make_circuit(bk_instrs)
    u_big = circuit.to_unitary()
    u_test = unitary_to_little_endian(u_big)
    assert np.allclose(u_expected, u_test)


@pytest.mark.parametrize("flat", [True, False])
@pytest.mark.parametrize("list_type", [True, False])
def test_gate_to_matrix_pytket(flat, list_type):
    """Test converting pytket gates to matrix"""
    c = TKCircuit(10, 2, name="example")
    c.CU1(np.pi / 2, 2, 3)

    c_unitary = _gate_to_matrix_pytket(
        gates=c.get_commands()[0] if list_type else c.get_commands(), flat=flat
    )
    if flat:
        assert c_unitary.shape[0] == 2**2
    else:
        assert c_unitary.shape[0] == 2**4


def test_unitary_raises():
    """Test raising ProgramTypeError for non-Circuit input"""
    with pytest.raises(ProgramTypeError):
        to_unitary(None)


def test_random_unitary():
    """Test generating random unitary"""
    matrix = random_unitary_matrix(2)
    assert np.allclose(matrix @ matrix.conj().T, np.eye(2))


def test_kronecker_product_factor_permutation():
    """Test calculating unitary permutation representing
    circuits with reversed qubits"""
    circuit = Circuit().h(0).cnot(0, 1)
    circuit_rev = Circuit().h(1).cnot(1, 0)

    unitary = circuit.to_unitary()
    unitary_rev = circuit_rev.to_unitary()

    assert np.allclose(rev_qubits_unitary(unitary), unitary_rev)


def test_kronecker_product_factor_permutation_invalid_input():
    """Test raising ValueError for non-square matrix of size not 2^N"""
    invalid_matrix = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    with pytest.raises(ValueError):
        rev_qubits_unitary(invalid_matrix)
