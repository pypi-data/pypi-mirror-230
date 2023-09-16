import subprocess
import tempfile
from os.path import join as join_path

import numpy as np
import pytest
from ase.build import bulk
from ase.calculators.emt import EMT
from ase.io import read
from ase.units import GPa

from calorine.nep import read_loss, read_nepfile, read_structures, setup_training


@pytest.fixture
def nep_parameters():
    return dict(version=4,
                type=[2, 'Au', 'Cu'],
                cutoff=[4, 4],
                n_max=[2, 1],
                l_max=[4, 0],
                lambda_1=0.1,
                lambda_2=0.2,
                lambda_e=1,
                lambda_f=5,
                lambda_v=0.2,
                neuron=2,
                generation=1000)


@pytest.fixture
def structures():
    structures = []

    structure = bulk('AuCu', crystalstructure='rocksalt', a=7.0)
    structure[0].z += 0.1
    structure.calc = EMT()
    structures.append(structure)

    structure = bulk('AuCu', crystalstructure='rocksalt', a=7.0)
    structure[0].z += 0.15
    structure.calc = EMT()
    structures.append(structure)

    return structures


@pytest.fixture
def setup_parameters():
    return dict(seed=42,
                n_splits=2,
                overwrite=True)


def test_nep_execution(nep_parameters, structures, setup_parameters):
    """This function tests running the nep executable with input generated
    by calorine. Since running the nep binary takes a couple of
    seconds to produce parseable output. The function contains
    multiple tests (rather than splitting them up in several different
    functions.)

    Note that this test requires the test runner to have a compatible GPU.
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        setup_parameters['rootdir'] = tmpdirname
        setup_training(nep_parameters, structures, **setup_parameters)

        path = join_path(setup_parameters['rootdir'], 'nepmodel_full')
        result = subprocess.run(['nep'], capture_output=True, cwd=path)
        assert 'Finished running nep.' in str(result.stdout)

        # check that read_loss runs
        _ = read_loss(join_path(path, 'loss.out'))

        # check that read_nepfile runs
        _ = read_nepfile(join_path(path, 'nep.in'))

        # test read_structures
        train_structures, test_structures = read_structures(path)
        train_structures_ref = read(join_path(path, 'train.xyz'), ':')
        test_structures_ref = read(join_path(path, 'test.xyz'), ':')

        assert len(train_structures) == len(train_structures_ref), \
            'number of training structures inconsistent'
        assert len(test_structures) == len(test_structures_ref), \
            'number of test structures inconsistent'

        for sref, s in zip(structures, train_structures + test_structures):
            assert len(sref) == len(s)
            assert np.allclose(sref.positions, s.positions, atol=1e-6)
            assert np.allclose(sref.get_forces(), s.get_forces(), atol=1e-6)
            assert np.allclose(sref.cell, s.cell, atol=1e-6)
            assert np.all(sref.symbols == s.symbols)

            for key in ['energy_predicted', 'energy_target',
                        'force_predicted', 'force_target',
                        'virial_predicted', 'virial_target',
                        'stress_predicted', 'stress_target']:
                assert key in s.info

            assert np.allclose(sref.get_forces(), s.info['force_target'], atol=1e-6)
            assert np.isclose(sref.get_potential_energy() / len(sref),
                              s.info['energy_target'], atol=1e-6)
            stress = -sref.get_stress() / GPa
            assert np.allclose(stress, s.info['stress_target'], atol=1e-6)
