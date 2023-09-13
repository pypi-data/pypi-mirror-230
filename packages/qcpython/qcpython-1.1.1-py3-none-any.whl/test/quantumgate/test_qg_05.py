from qcpy.quantumgate import hadamard
import numpy as np


def test_qg_05():
    assert (
        hadamard() == np.array([
            [1 + 0j, 1 + 0j],
            [1 + 0j, -1 + 0j]
        ], 'F') * (1 / np.sqrt(2))
    ).all(), 'test_qg_05 Failed on Hadamard'
