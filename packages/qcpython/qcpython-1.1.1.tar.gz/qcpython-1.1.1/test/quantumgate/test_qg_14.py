from qcpy.quantumgate import rz
import numpy as np


def test_qg_14():
    assert (
        rz() == np.array([
            [np.exp((0 - 1j * ((np.pi / 2) / 2))), 0 + 0j],
            [0 + 0j, np.exp(0 + 1j * ((np.pi / 2) / 2))]
        ], 'F')
    ).all(), 'test_qg_14 Failed on Rz'
