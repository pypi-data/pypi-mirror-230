from os.path import exists
from os.path import join as join_path

import numpy as np
import pytest
from ase.build import bulk
from ase.calculators.emt import EMT
from ase.io import read

from calorine.nep import read_nepfile, setup_training


@pytest.fixture
def nep_parameters():
    return dict(version=3,
                type=[2, 'Au', 'Cu'],
                cutoff=[8, 4],
                n_max=[8, 6],
                l_max=[4, 0],
                lambda_1=0.1,
                lambda_2=0.2,
                lambda_e=1,
                lambda_f=5,
                lambda_v=0.2,
                neuron=50,
                generation=200000)


@pytest.fixture
def structures():
    structures = []
    for i, alat in enumerate(np.arange(3, 6, 0.1)):
        structure = bulk('AuCu', crystalstructure='rocksalt', a=alat)
        structure.calc = EMT()
        structure.info['index'] = i
        structures.append(structure)
    return structures


@pytest.fixture
def setup_parameters():
    return dict(rootdir='test_dir',
                seed=42,
                n_splits=3,
                overwrite=True)


def test_setup_training(nep_parameters, structures, setup_parameters):
    setup_training(nep_parameters, structures, **setup_parameters)
    rootdir = setup_parameters['rootdir']
    n_splits = setup_parameters['n_splits']
    assert exists(rootdir), 'Root directory not created'

    path = join_path(rootdir, 'nepmodel_full')
    assert exists(path), 'nepmodel_full subdirectory not created'
    assert exists(join_path(path, 'train.xyz')), 'Training structures not written'
    assert exists(join_path(path, 'test.xyz')), 'Testing structures not written'
    assert exists(join_path(path, 'nep.in')), 'nep.in not written'

    train_structures = read(join_path(path, 'train.xyz'), ':')
    test_structures = read(join_path(path, 'test.xyz'), ':')
    assert len(train_structures) == len(structures), \
        'Incorrect number of training structures generated'
    assert len(test_structures) == 1, \
        'Incorrect number of test structures generated'

    all_test_structures = []
    for k in range(1, n_splits + 1):
        path = join_path(rootdir, f'nepmodel_split{k}')
        assert exists(path), f'nepmodel_split{k} subdirectory not created'
        assert exists(join_path(path, 'train.xyz')), 'Training structures not written'
        assert exists(join_path(path, 'test.xyz')), 'Testing structures not written'
        assert exists(join_path(path, 'nep.in')), 'nep.in not written'

        train_structures = read(join_path(path, 'train.xyz'), ':')
        test_structures = read(join_path(path, 'test.xyz'), ':')
        test_size = int((1/n_splits) * len(structures))
        train_size = len(structures) - test_size
        assert len(train_structures) == train_size, \
            'Incorrect number of training structures generated'
        assert len(test_structures) == test_size, \
            'Incorrect number of test structures generated'
        all_test_structures.extend(test_structures)
    # make sure that all structures have been in the test set exactly once
    assert len(all_test_structures) == len(structures)
    indices = [s.info['index'] for s in structures]
    test_indices = [ts.info['index'] for ts in all_test_structures]
    assert len(set(test_indices)) == len(structures)
    assert set(indices) == set(test_indices)


def test_setup_training_existing_dir_no_overwrite(nep_parameters, structures, setup_parameters):
    setup_parameters['overwrite'] = False
    with pytest.raises(FileExistsError) as excinfo:
        setup_training(nep_parameters, structures, **setup_parameters)
    assert 'Output directory exists. Set overwrite=True in' \
        ' order to override this behavior.' in str(excinfo.value), \
        'Incorrect error message for existing directory with no overwrite'


def test_setup_training_invalid_n_splits(nep_parameters, structures, setup_parameters):
    setup_parameters['n_splits'] = 31
    with pytest.raises(ValueError) as excinfo:
        setup_training(nep_parameters, structures, **setup_parameters)
    assert 'n_splits (31) must be positive and must not exceed' in str(excinfo.value), \
        'Incorrect error message for invalid value for n_splits'


def test_setup_training_n_splits_is_none(nep_parameters, structures, setup_parameters):
    setup_parameters['n_splits'] = None
    setup_training(nep_parameters, structures, **setup_parameters)
    path = join_path(setup_parameters['rootdir'], 'nepmodel_full')
    train_structures = read(join_path(path, 'train.xyz'), ':')
    test_structures = read(join_path(path, 'test.xyz'), ':')
    assert len(train_structures) == len(structures), \
        'Incorrect number of training structures generated'
    assert len(test_structures) == 1, \
        'Incorrect number of test structures generated'


def test_setup_training_nep_parameters(nep_parameters, structures, setup_parameters):
    setup_parameters['n_splits'] = None
    setup_training(nep_parameters, structures, **setup_parameters)
    path = join_path(setup_parameters['rootdir'], 'nepmodel_full')
    rec = read_nepfile(join_path(path, 'nep.in'))
    for key, val_ref in nep_parameters.items():
        assert key in rec, f'{key} missing from nep.in'
        val_read = rec[key]
        assert np.all(val_read == val_ref), f'{key} incorrectly written'
