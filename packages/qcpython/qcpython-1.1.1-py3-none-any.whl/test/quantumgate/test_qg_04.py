from qcpy.quantumgate import pauliz
import numpy as np


def test_qg_04():
    assert (
        pauliz() == np.array([
            [1 + 0j, 0 + 0j],
            [0 + 0j, -1 + 0j]
        ], 'F')
    ).all(), 'test_qg_04 Failed on PauliZ'
