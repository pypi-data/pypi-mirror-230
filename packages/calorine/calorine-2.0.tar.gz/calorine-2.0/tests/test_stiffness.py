import numpy as np
import os
import pytest
from ase.build import bulk
from ase.calculators.emt import EMT
from calorine.calculators import CPUNEP
from calorine.tools import get_elastic_stiffness_tensor


@pytest.fixture
def fcc_aluminum():
    structure = bulk('Al', 'fcc', a=4.05, cubic=True)
    structure.calc = EMT()
    return structure


@pytest.fixture
def diamond_aluminum():
    structure = bulk('Al', 'diamond', a=7.2, cubic=True)
    structure.calc = EMT()
    return structure


@pytest.fixture
def rocksalt():
    structure = bulk('PbTe', 'rocksalt', a=4.18, cubic=True)
    model_path = os.path.join('tests', 'nep_models', 'nep3_v3.3.1_PbTe_Fan22.txt')
    structure.calc = CPUNEP(model_path)
    return structure


@pytest.fixture
def zincblende():
    structure = bulk('PbTe', 'zincblende', a=9.9, cubic=True)
    model_path = os.path.join('tests', 'nep_models', 'nep3_v3.3.1_PbTe_Fan22.txt')
    structure.calc = CPUNEP(model_path)
    return structure


def get_reference_data(structure_name, clamped, epsilon):
    if structure_name == 'fcc_aluminum' and clamped is False and epsilon == 0.01:
        return np.array([[47.638, 30.753, 30.753, -0.000, 0.000, 0.000],
                         [30.753, 47.638, 30.753, -0.000, -0.000, -0.000],
                         [30.753, 30.753, 47.638, 0.000, 0.000, -0.000],
                         [-0.000, -0.000, 0.000, 31.773, -0.000, 0.000],
                         [0.000, -0.000, 0.000, -0.000, 31.773, -0.000],
                         [0.000, -0.000, -0.000, 0.000, -0.000, 31.773]])

    elif structure_name == 'diamond_aluminum' and clamped is False and epsilon == 0.01:
        return np.array([[-687.249, 3.323, 3.323, -0.000, 0.000, -0.000],
                         [3.323, -687.249, 3.323, 0.000, -0.000, 0.000],
                         [3.323, 3.323, -687.249, 0.000, -0.000, 0.000],
                         [-0.000, 0.000, 0.000, -1318.260, 0.000, -0.000],
                         [0.000, -0.000, -0.000, 0.000, -1318.260, 0.000],
                         [0.000, 0.000, 0.000, -0.000, 0.000, -1318.260]])

    elif structure_name == 'diamond_aluminum' and clamped is True and epsilon == 0.01:
        return np.array([[5.811, 3.323, 3.323, 0.000, -0.000, -0.000],
                         [3.323, 5.811, 3.323, 0.000, -0.000, -0.000],
                         [3.323, 3.323, 5.811, -0.000, -0.000, 0.000],
                         [0.000, 0.000, -0.000, -3.016, 0.000, -0.000],
                         [-0.000, -0.000, -0.000, 0.000, -3.016, 0.000],
                         [-0.000, -0.000, 0.000, -0.000, 0.000, -3.016]])

    elif structure_name == 'rocksalt' and clamped is False and epsilon == 0.01:
        return np.array([[951.310, 104.841, 104.841, -0.000, -0.000, -0.000],
                         [104.841, 951.310, 104.841, -0.000, 0.000, 0.000],
                         [104.841, 104.841, 951.310, -0.000, 0.000, 0.000],
                         [-0.000, -0.000, -0.000, 70.814, 0.000, -0.000],
                         [-0.000, 0.000, 0.000, 0.000, 70.814, 0.000],
                         [-0.000, 0.000, 0.000, -0.000, 0.000, 70.814]])

    elif structure_name == 'rocksalt' and clamped is False and epsilon == 0.02:
        return np.array([[935.748, 99.310, 99.310, 0.000, 0.000, -0.000],
                         [99.310, 935.748, 99.310, -0.000, 0.000, -0.000],
                         [99.310, 99.310, 935.748, 0.000, 0.000, -0.000],
                         [0.000, -0.000, 0.000, 70.987, -0.000, -0.000],
                         [0.000, 0.000, 0.000, -0.000, 70.987, 0.000],
                         [-0.000, -0.000, -0.000, -0.000, 0.000, 70.987]])

    elif structure_name == 'zincblende' and clamped is False and epsilon == 0.01:
        return np.array([[1.372, 1.040, 1.040, -0.000, 0.000, 0.000],
                         [1.040, 1.372, 1.040, -0.000, -0.000, -0.000],
                         [1.040, 1.040, 1.372, -0.000, 0.000, -0.000],
                         [-0.000, -0.000, -0.000, 0.440, -0.000, -0.000],
                         [0.000, -0.000, 0.000, -0.000, 0.440, 0.000],
                         [0.000, 0.000, 0.000, 0.000, 0.000, 0.440]])

    elif structure_name == 'zincblende' and clamped is False and epsilon == 0.02:
        return np.array([[1.382, 1.054, 1.054, 0.000, -0.000, 0.000],
                         [1.054, 1.382, 1.054, -0.000, 0.000, -0.000],
                         [1.054, 1.054, 1.382, -0.000, -0.000, -0.000],
                         [-0.000, -0.000, -0.000, 0.442, 0.000, -0.000],
                         [-0.000, -0.000, -0.000, 0.000, 0.442, 0.000],
                         [-0.000, 0.000, 0.000, 0.000, 0.000, 0.442]])

    elif structure_name == 'zincblende' and clamped is True and epsilon == 0.01:
        return np.array([[1.372, 1.040, 1.040, 0.000, 0.000, 0.000],
                         [1.040, 1.372, 1.040, -0.000, -0.000, -0.000],
                         [1.040, 1.040, 1.372, -0.000, -0.000, -0.000],
                         [-0.000, -0.000, -0.000, 0.748, 0.000, -0.000],
                         [-0.000, -0.000, -0.000, 0.000, 0.748, -0.000],
                         [0.000, -0.000, 0.000, 0.000, 0.000, 0.748]])

    elif structure_name == 'zincblende' and clamped is True and epsilon == 0.02:
        return np.array([[1.381, 1.054, 1.054, 0.000, 0.000, 0.000],
                         [1.054, 1.381, 1.054, 0.000, -0.000, 0.000],
                         [1.054, 1.054, 1.381, -0.000, 0.000, -0.000],
                         [-0.000, 0.000, -0.000, 0.746, -0.000, -0.000],
                         [-0.000, -0.000, -0.000, -0.000, 0.746, -0.000],
                         [-0.000, 0.000, 0.000, 0.000, 0.000, 0.746]])


@pytest.mark.parametrize('structure_name,clamped,epsilon',
                         [
                             ('fcc_aluminum', False, 0.01),
                             ('diamond_aluminum', False, 0.01),
                             ('diamond_aluminum', True, 0.01),
                             ('rocksalt', False, 0.01),
                             ('rocksalt', False, 0.02),
                             ('zincblende', False, 0.01),
                             ('zincblende', False, 0.02),
                             ('zincblende', True, 0.01),
                             ('zincblende', True, 0.02),
                         ])
def test_get_elastic_stiffness_tensor(structure_name, clamped, epsilon, request):
    structure = request.getfixturevalue(structure_name)
    C_ref = get_reference_data(structure_name, clamped, epsilon)

    # Compute the elastic stiffness tensor
    C = get_elastic_stiffness_tensor(structure, clamped=clamped, epsilon=epsilon)

    # Compare to reference values
    assert np.isclose(C, C_ref, atol=0.1).all()

    # Check that the shape of the tensor is correct
    assert C.shape
