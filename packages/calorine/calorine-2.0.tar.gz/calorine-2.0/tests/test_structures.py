import numpy as np
import pytest
from ase.build import bulk
from ase.calculators.emt import EMT
from calorine.tools import relax_structure


@pytest.fixture
def structure():
    structure = bulk('Ag', a=4, cubic=True)
    structure[0].position += np.array([0.03, 0.08, 0])
    structure.calc = EMT()
    return structure


@pytest.mark.parametrize('minimizer, constant_cell, constant_volume, cell', [
    (
        'bfgs',
        False,
        False,
        [[4.064344467646021, 0.00010293213753658188, 0],
         [0.00010293213753565035, 4.063399911533125, 0],
         [0, 0, 4.064486069840965]]
    ),
    (
        'bfgs',
        False,
        True,
        [[4.000296209078849, -0.00023363048485108715, 0],
         [-0.000233630484850003, 3.9992734453197674, 0],
         [0, 0, 4.000430459369042]]
    ),
    (
        'lbfgs',
        False,
        True,
        [[4.000296209078849, -0.00023363048485108715, 0],
         [-0.000233630484850003, 3.9992734453197674, 0],
         [0, 0, 4.000430459369042]]
    ),
    (
        'fire',
        True,
        False,  # Volume is fixed if cell is fixed
        [[4.0, 0.0, 0.0],
         [0.0, 4.0, 0.0],
         [0.0, 0.0, 4.0]]
    ),
    (
        'bfgs-scipy',
        False,
        True,
        [[4.000288933940351, 0.0004604843003583068, 0],
         [0.00046048430035830777, 3.9992704548874647, 0],
         [0, 0, 4.000440765444412]]
    ),
    (
        'gpmin',
        False,
        True,
        [[3.9994073553656007, -0.0006934672576998964, 0],
         [-0.0006934672576774285, 4.00125729962704, 0],
         [0, 0, 3.9993357618357335]]
    ),
])
def test_check_fmax(structure,
                    minimizer,
                    constant_cell,
                    constant_volume,
                    cell):
    """Tests that a structure is relaxed to a maximum force lower than the specified threshold."""
    pos_pre_relax = structure.get_positions()

    relax_structure(
        structure,
        fmax=0.02,
        steps=1000,
        minimizer=minimizer,
        constant_cell=constant_cell,
        constant_volume=constant_volume,
    )

    fmax_post_relax = np.max(np.linalg.norm(structure.get_forces(), axis=1))
    assert fmax_post_relax < 0.03
    assert not np.allclose(structure.positions, pos_pre_relax)  # Make sure that the atoms moved
    assert np.isclose(structure.get_volume(), np.linalg.det(cell), atol=1e-4)
    assert np.allclose(structure.get_cell(), cell, atol=1e-4)


@pytest.mark.parametrize('with_calculator, minimizer, error',
                         [
                             (False, 'fire', 'Structure has no attached calculator object'),
                             (True, 'invalid', 'Unknown minimizer: invalid'),
                          ]
                         )
def test_no_calculator(structure, with_calculator, minimizer, error):
    if not with_calculator:
        structure.calc = None
    with pytest.raises(ValueError) as e:
        relax_structure(structure, minimizer=minimizer)
    assert error in str(e)
