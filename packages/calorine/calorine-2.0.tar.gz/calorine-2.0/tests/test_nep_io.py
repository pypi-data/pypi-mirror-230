import shutil
from pathlib import Path

import numpy as np
import pytest
from ase import Atoms
from ase.build import bulk
from ase.calculators.lj import LennardJones
from ase.calculators.singlepoint import SinglePointCalculator
from ase.io import read
from ase.stress import full_3x3_to_voigt_6_stress, voigt_6_to_full_3x3_stress

from calorine.nep import get_parity_data, read_loss, read_nepfile, read_structures, write_structures
from calorine.nep.io import _read_data_file


@pytest.fixture
def PbTe():
    PbTeBulk = bulk('PbTe', crystalstructure='rocksalt', a=4)
    PbTeBulk[0].position += np.array([0.03, 0.02, 0])
    return PbTeBulk


@pytest.fixture
def TenPbTeWithInfo(PbTe):
    n_structures = 10
    structures = []
    for i in range(n_structures):
        # Test with differently sized structures in the test set
        atoms = PbTe.copy().repeat(i + 1)
        natoms = len(atoms)
        atoms.info['energy_target'] = float(i)
        atoms.info['energy_predicted'] = float(i)
        atoms.info['force_target'] = np.arange(i, natoms * 3 + i).reshape((natoms, 3))
        atoms.info['force_predicted'] = np.arange(i, natoms * 3 + i).reshape(
            (natoms, 3)
        )
        atoms.info['virial_target'] = -np.arange(i, 6 + i).reshape(6)
        atoms.info['virial_predicted'] = -np.arange(i, 6 + i).reshape(6)
        atoms.info['stress_target'] = -np.arange(i, 6 + i).reshape(6)
        atoms.info['stress_predicted'] = -np.arange(i, 6 + i).reshape(6)

        atoms.info['polarizability_target'] = -np.arange(i + 1, 6 + i + 1).reshape(6)
        atoms.info['polarizability_predicted'] = -np.arange(i + 1, 6 + i + 1).reshape(6)
        atoms.info['dipole_target'] = -np.arange(i + 2, 6 + i + 2).reshape(6)
        atoms.info['dipole_predicted'] = -np.arange(i + 2, 6 + i + 2).reshape(6)
        structures.append(atoms)
    return structures


def sel2idx(select: str) -> int:
    map = {'x': 0, 'y': 1, 'z': 2, 'xx': 0, 'yy': 1, 'zz': 2, 'yz': 3, 'xz': 4, 'xy': 5}
    return map[select]


# --- read_nepfile ---
def test_read_nepfile_unknown_setting(tmpdir):
    """Reads a nep.in file with a comment"""
    p = tmpdir.join('nep.in')
    p.write('test 1\n')
    settings = read_nepfile(str(p))
    assert settings['test'] == '1'


def test_read_nepfile_run_comment(tmpdir):
    """Reads a nep.in file with a comment"""
    p = tmpdir.join('nep.in')
    p.write('#basis_size 10 6\n')
    settings = read_nepfile(str(p))
    assert settings == {}


def test_read_nepfile_nep():
    """Reads a nep.in file"""
    settings = read_nepfile('tests/example_files/nep.in')
    assert settings['version'] == 4
    assert settings['type'] == [2, 'C', 'H']
    assert settings['cutoff'] == [8, 4]
    assert settings['n_max'] == [8, 6]
    assert settings['l_max'] == [4]
    assert settings['neuron'] == 50
    assert settings['lambda_1'] == 0.01
    assert settings['lambda_2'] == 0.01
    assert settings['batch'] == 100
    assert settings['population'] == 50
    assert settings['generation'] == 50000
    assert settings['lambda_e'] == 1
    assert 'lambda_f' not in settings.keys()


def test_read_nepfile_nep_blank_line(tmpdir):
    """Reads a nep.in file with a blank line"""
    p = tmpdir.join('nep.in')
    p.write('\n')
    settings = read_nepfile(str(p))
    assert settings == {}


# --- read_loss ---
def test_read_loss():
    """Reads a loss.out file"""
    loss = read_loss('tests/example_files/loss.out')
    columns_check = loss.columns == [
        'total_loss',
        'L1',
        'L2',
        'RMSE_E_train',
        'RMSE_F_train',
        'RMSE_V_train',
        'RMSE_E_test',
        'RMSE_F_test',
        'RMSE_V_test',
    ]
    assert columns_check.all()
    assert isinstance(loss.index[0], int)
    assert loss.index[0] == 100
    assert len(loss) == 95


# --- read_loss ---
def test_read_loss_polarizability():
    """Reads a loss.out file"""
    loss = read_loss('tests/example_files/loss_polarizability.out')
    columns_check = loss.columns == [
        'total_loss',
        'L1',
        'L2',
        'RMSE_P_train',
        'RMSE_P_test',
    ]
    assert columns_check.all()
    assert isinstance(loss.index[0], int)
    assert loss.index[0] == 100
    assert len(loss) == 95


def test_read_loss_single_row(tmpdir):
    """Tries to read a loss.out file that has only a single row"""
    p = tmpdir.join('loss.out')
    p.write('100 2 3 4 5 6 7 8 9 10\n')
    loss = read_loss(str(p))
    columns_check = loss.columns == [
        'total_loss',
        'L1',
        'L2',
        'RMSE_E_train',
        'RMSE_F_train',
        'RMSE_V_train',
        'RMSE_E_test',
        'RMSE_F_test',
        'RMSE_V_test',
    ]
    assert columns_check.all()
    assert isinstance(loss.index[0], int)
    assert loss.index[0] == 100


def test_read_loss_single_polarizability_row(tmpdir):
    """Tries to read a loss.out file that has only a single row"""
    p = tmpdir.join('loss.out')
    p.write('100 2 3 4 5 6\n')
    loss = read_loss(str(p))
    columns_check = loss.columns == [
        'total_loss',
        'L1',
        'L2',
        'RMSE_P_train',
        'RMSE_P_test',
    ]
    assert columns_check.all()
    assert isinstance(loss.index[0], int)
    assert loss.index[0] == 100


def test_read_loss_malformed_file(tmpdir):
    """Tries to read a malformed loss.out file"""
    p = tmpdir.join('loss_invalid.out')
    p.write('0 0 0 0 0 0 0\n')
    with pytest.raises(ValueError, match='Input file contains 7 data columns'):
        read_loss(str(p))


# --- write_structures ---
def test_write_structures_single_structure(tmpdir, PbTe):
    """Writes a structure to a extxyz-file"""
    p = tmpdir.join('train.xyz')
    PbTe.calc = LennardJones()
    write_structures(str(p), [PbTe])
    read_structure = read(str(p), format='extxyz')
    assert np.isclose(
        read_structure.cell.volume, PbTe.cell.volume, atol=1e-12, rtol=1e-6
    )
    assert np.isclose(
        read_structure.get_potential_energy(),
        PbTe.get_potential_energy(),
        atol=1e-12,
        rtol=1e-6,
    )
    assert np.allclose(read_structure.positions, PbTe.positions, atol=1e-12, rtol=1e-6)
    assert np.allclose(
        read_structure.get_forces(), PbTe.get_forces(), atol=1e-12, rtol=1e-6
    )
    # Written accuracy is around 2e-6
    assert np.allclose(
        read_structure.get_stress(), PbTe.get_stress(voigt=True), atol=1e-12, rtol=1e-5
    )


def test_write_structures_with_weight(tmpdir, PbTe):
    """Writes structures with weight to an extxyz-file"""
    p = tmpdir.join('train.xyz')
    structure1 = PbTe.copy()
    structure2 = PbTe.copy()
    structure1.calc = LennardJones()
    structure2.calc = LennardJones()
    structure1.info['weight'] = 1
    structure2.info['weight'] = 50
    write_structures(str(p), [structure1, structure2])
    with open(str(p), 'r') as f:
        lines = f.readlines()
        assert 'weight=1' in lines[1]
        assert 'weight=50' in lines[5]


def test_write_structure_with_filename(tmpdir, PbTe):
    """Writes with a filename to an extxyz-file"""
    p = tmpdir.join('train.xyz')
    PbTe.calc = LennardJones()
    PbTe.info['filename'] = 'result.testcar'
    write_structures(str(p), [PbTe])
    read_structure = read(str(p), format='extxyz')
    print(read_structure.info)
    assert read_structure.info['filename'] == 'result.testcar'
    with open(str(p), 'r') as f:
        lines = f.readlines()
        assert 'filename=result.testcar' in lines[1]


def test_write_structure_without_energy_or_forces(tmpdir):
    """Tries to write a structure without a calculator attached"""
    p = tmpdir.join('train.xyz')
    C = Atoms('C', positions=[(0, 0, 0)])
    with pytest.raises(RuntimeError) as e:
        write_structures(str(p), [C])
    assert 'Failed to retrieve energy and/or forces for structure' in str(e)


def test_write_structure_without_cell(tmpdir):
    """Tries to write a structure without a proper cell"""
    p = tmpdir.join('train.xyz')
    C = Atoms('C', positions=[(0, 0, 0)])
    C.calc = LennardJones()
    with pytest.raises(ValueError) as e:
        write_structures(str(p), [C])
    assert 'You have 0 lattice vectors: volume not defined' in str(e)


def test_write_structure_with_zero_cell_volume(tmpdir):
    """Tries to write a structure without a proper celld"""
    p = tmpdir.join('train.xyz')
    C = Atoms('C', positions=[(0, 0, 0)], cell=[1e-12, 1e-12, 1e-12])
    C.calc = LennardJones()
    with pytest.raises(ValueError) as e:
        write_structures(str(p), [C])
    assert 'Structure cell must have a non-zero volume' in str(e)


# get_parity_data
@pytest.mark.parametrize('property', ['energy', 'force', 'virial', 'stress'])
def test_get_parity_data(property, TenPbTeWithInfo):
    """Extracts parity data from a list of structures"""
    df = get_parity_data(structures=TenPbTeWithInfo, property=property, flatten=False)
    assert np.all(df.columns == ['predicted', 'target'])
    assert len(df['target']) == 10
    assert len(df['target']) == len(df['predicted'])
    if not property == 'energy':
        assert df['target'][0].shape == df['predicted'][0].shape


@pytest.mark.parametrize(
    'property, selection',
    [('force', ['x']), ('virial', ['x', 'y', 'z']), ('stress', ['xx', 'yy', 'zz'])],
)
def test_get_parity_data_diagonal_components(TenPbTeWithInfo, property, selection):
    """Extracts parity data from a list of structures, selecting properties on the diagonal."""
    df = get_parity_data(
        structures=TenPbTeWithInfo, property=property, selection=selection, flatten=False
    )
    for i, structure in enumerate(TenPbTeWithInfo):
        assert len(df['target'][i]) == len(selection)
        assert len(df['target'][i]) == len(df['predicted'][i])
        for j, select in enumerate(selection):
            if property == 'force':
                expected_target = structure.info[f'{property}_target'][
                    :, sel2idx(select)
                ]
                expected_predicted = structure.info[f'{property}_predicted'][
                    :, sel2idx(select)
                ]
            elif property in ('virial', 'stress'):
                expected_target = structure.info[f'{property}_target'][sel2idx(select)]
                expected_predicted = structure.info[f'{property}_predicted'][
                    sel2idx(select)
                ]
            assert np.all(df['target'][i][j] == expected_target)
            assert np.all(df['predicted'][i][j] == expected_predicted)


@pytest.mark.parametrize(
    'property, selection',
    [('virial', ['yz', 'xz', 'xy']), ('stress', ['yz', 'xz', 'xy'])],
)
def test_get_parity_data_off_diagonal_components(TenPbTeWithInfo, property, selection):
    """Extracts parity data from a list of structures, selecting properties on the off-diagonal."""
    df = get_parity_data(
        structures=TenPbTeWithInfo, property=property, selection=selection, flatten=False
    )
    for i, structure in enumerate(TenPbTeWithInfo):
        assert len(df['target'][i]) == len(selection)
        assert len(df['target'][i]) == len(df['predicted'][i])
        for j, select in enumerate(selection):
            expected_target = structure.info[f'{property}_target'][sel2idx(select)]
            expected_predicted = structure.info[f'{property}_predicted'][
                sel2idx(select)
            ]
            assert np.all(df['target'][i][j] == expected_target)
            assert np.all(df['predicted'][i][j] == expected_predicted)


@pytest.mark.parametrize(
    'property, selection',
    [('polarizability', ['x', 'y', 'z']), ('polarizability', ['xx', 'yy', 'zz'])],
)
def test_get_parity_data_polarizability_components(
    TenPbTeWithInfo, property, selection
):
    """Extracts parity data from a list of structures, selecting properties on the diagonal."""
    df = get_parity_data(
        structures=TenPbTeWithInfo, property=property, selection=selection, flatten=False
    )
    for i, structure in enumerate(TenPbTeWithInfo):
        assert len(df['target'][i]) == len(selection)
        assert len(df['target'][i]) == len(df['predicted'][i])
        for j, select in enumerate(selection):
            expected_target = structure.info[f'{property}_target'][sel2idx(select)]
            expected_predicted = structure.info[f'{property}_predicted'][
                sel2idx(select)
            ]
        assert np.all(df['target'][i][j] == expected_target)
        assert np.all(df['predicted'][i][j] == expected_predicted)


@pytest.mark.parametrize(
    'property, selection',
    [('dipole', ['x', 'y', 'z']), ('dipole', ['xx', 'yy', 'zz'])],
)
def test_get_parity_data_dipole_components(TenPbTeWithInfo, property, selection):
    """Extracts parity data from a list of structures, selecting properties on the diagonal."""
    df = get_parity_data(
        structures=TenPbTeWithInfo, property=property, selection=selection, flatten=False
    )
    for i, structure in enumerate(TenPbTeWithInfo):
        assert len(df['target'][i]) == len(selection)
        assert len(df['target'][i]) == len(df['predicted'][i])
        for j, select in enumerate(selection):
            expected_target = structure.info[f'{property}_target'][sel2idx(select)]
            expected_predicted = structure.info[f'{property}_predicted'][
                sel2idx(select)
            ]
        assert np.all(df['target'][i][j] == expected_target)
        assert np.all(df['predicted'][i][j] == expected_predicted)


@pytest.mark.parametrize(
    'property, selection',
    [('force', ['abs']), ('virial', ['abs']), ('stress', ['abs'])],
)
def test_get_parity_data_abs(TenPbTeWithInfo, property, selection):
    """Extracts parity data from a list of structures, calculating the absolute value"""
    df = get_parity_data(
        structures=TenPbTeWithInfo, property=property, selection=selection, flatten=False
    )
    for i, structure in enumerate(TenPbTeWithInfo):
        assert len(df['target'][i]) == len(selection)
        assert len(df['target'][i]) == len(df['predicted'][i])
        for j, _ in enumerate(selection):
            if property == 'force':
                expected_target = np.linalg.norm(
                    structure.info[f'{property}_target'], axis=1
                )
                expected_predicted = np.linalg.norm(
                    structure.info[f'{property}_predicted'], axis=1
                )
            elif property in ('virial', 'stress'):
                expected_target = np.linalg.norm(
                    voigt_6_to_full_3x3_stress(structure.info[f'{property}_target'])
                )
                expected_predicted = np.linalg.norm(
                    voigt_6_to_full_3x3_stress(structure.info[f'{property}_predicted'])
                )
            assert np.all(df['target'][i][j] == expected_target)
            assert np.all(df['predicted'][i][j] == expected_predicted)


@pytest.mark.parametrize('property, selection', [('stress', ['pressure'])])
def test_get_parity_data_pressure(TenPbTeWithInfo, property, selection):
    """Extracts parity data from a list of structures, calculating the pressure"""
    df = get_parity_data(
        structures=TenPbTeWithInfo, property=property, selection=selection, flatten=False
    )
    for i, structure in enumerate(TenPbTeWithInfo):
        assert len(df['target'][i]) == len(selection)
        assert len(df['target'][i]) == len(df['predicted'][i])
        for j, _ in enumerate(selection):
            expected_target = -np.sum(structure.info[f'{property}_target'][:3]) / 3
            expected_predicted = (
                -np.sum(structure.info[f'{property}_predicted'][:3]) / 3
            )
            assert np.all(df['target'][i][j] == expected_target)
            assert np.all(df['predicted'][i][j] == expected_predicted)


@pytest.mark.parametrize(
    'property, selection, output',
    [
        ('energy', ['x'], 'Selection does nothing for scalar-valued `energy`.'),
        ('force', ['pressure'], 'Cannot calculate pressure for `force`.'),
        ('force', ['xy'], 'Selection `xy` is not compatible with property `force`.'),
        ('virial', ['zy'], 'Selection `zy` is not allowed.'),
    ],
)
def test_get_parity_data_invalid_selection(
    TenPbTeWithInfo, property, selection, output
):
    """Tries to extract parity data from structures with an invalid selection"""
    with pytest.raises(ValueError) as e:
        get_parity_data(
            structures=TenPbTeWithInfo, property=property, selection=selection, flatten=True
        )
    assert output in str(e)


@pytest.mark.parametrize(
    'property, output',
    [
        (
            'bounciness',
            "`property` must be one of 'energy', 'force', 'virial', 'stress',"
            " 'polarizability', 'dipole'.",  # noqa
        ),
    ],
)
def test_get_parity_data_invalid_property(TenPbTeWithInfo, property, output):
    """Tries to extract parity data from structures with an invalid property"""
    with pytest.raises(ValueError) as e:
        get_parity_data(structures=TenPbTeWithInfo, property=property, flatten=False)
    assert output in str(e)


def test_get_parity_data_missing_info():
    """Raises error when property(ies) is missing in atom info dictionary"""
    n_structures = 10
    structures = []
    for _ in range(n_structures):
        # Test with differently sized structures in the test set
        natoms = np.random.randint(1, 10)
        atoms = Atoms('C' * natoms)
        atoms.info['energy_target'] = 1.0
        structures.append(atoms)
    with pytest.raises(KeyError) as e:
        get_parity_data(structures, property='energy', flatten=True)
    assert 'energy_predicted does not exist in info object!' in str(e)


@pytest.mark.parametrize(
    'property, count_wo_flatten, count_with_flatten',
    [
        ('energy', 10, 10),
        ('force', 10, 18150),
        ('virial', 10, 60),
    ],
)
def test_get_parity_data_flatten(
    property, count_wo_flatten, count_with_flatten, TenPbTeWithInfo
):
    """Checks the option to flatten the data."""
    df_wo_flatten = get_parity_data(
        structures=TenPbTeWithInfo, property=property, flatten=False
    )
    assert len(df_wo_flatten) == count_wo_flatten
    df_with_flatten = get_parity_data(
        structures=TenPbTeWithInfo, property=property, flatten=True
    )
    assert len(df_with_flatten) == count_with_flatten


def _write_mock_nep_files(fname, quantity, shape):
    with open(fname, 'w') as fd:
        if shape == 1:
            for q in quantity:
                fd.write(f'{q:.5f} {q - 1:.5f}\n')
        elif shape == 3:
            for q in quantity:
                for n in range(q.shape[0]):
                    _q = q[n]
                    fd.write(
                        f'{_q[0]:.5f} {_q[1]:.5f} {_q[2]:.5f}'
                        f' {_q[0] - 1:.5f} {_q[1] - 1:.5f} {_q[2] - 1:.5f}\n'
                    )
        elif shape == 6:
            for q in quantity:
                fd.write(
                    f'{q[0]:.5f} {q[1]:.5f} {q[2]:.5f}'
                    f' {q[3]:.5f} {q[4]:.5f} {q[5]:.5f}'
                    f' {q[0] - 1:.5f} {q[1] - 1:.5f} {q[2] - 1:.5f}'
                    f' {q[3] - 1:.5f} {q[4] - 1:.5f} {q[5] - 1:.5f}\n'
                )
        else:
            raise ValueError('Wrong shape on input')


def _get_mock_nep_atoms(**kwargs):
    atom = bulk('C', crystalstructure='diamond', a=3.57)
    stress = full_3x3_to_voigt_6_stress(np.random.random(size=(3, 3)))
    calc = SinglePointCalculator(
        atom,
        energy=np.random.random(),
        forces=np.random.random(size=(2, 3)),
        stress=stress,
    )
    if kwargs:
        for key, val in kwargs.items():
            calc.results[key] = np.array(val, float)
    atom.calc = calc
    return atom


def test_read_structures_potential(tmpdir):
    """Read energy_*.out, force_*.out, stress_*.out file"""
    p = tmpdir.join('nep.in')
    p.write('mode 0\n')

    atoms_test = [_get_mock_nep_atoms() for _ in range(4)]
    atoms_train = [_get_mock_nep_atoms() for _ in range(7)]

    energy_train = tmpdir.join('energy_train.out')
    forces_train = tmpdir.join('force_train.out')
    virial_train = tmpdir.join('virial_train.out')
    energy_test = tmpdir.join('energy_test.out')
    forces_test = tmpdir.join('force_test.out')
    virial_test = tmpdir.join('virial_test.out')

    write_structures(tmpdir.join('test.xyz'), atoms_test)
    write_structures(tmpdir.join('train.xyz'), atoms_train)

    _write_mock_nep_files(
        energy_test, [a.get_potential_energy() for a in atoms_test], 1
    )
    _write_mock_nep_files(forces_test, [a.get_forces() for a in atoms_test], 3)
    _write_mock_nep_files(virial_test, [a.get_stress() for a in atoms_test], 6)
    _write_mock_nep_files(
        energy_train, [a.get_potential_energy() for a in atoms_train], 1
    )
    _write_mock_nep_files(forces_train, [a.get_forces() for a in atoms_train], 3)
    _write_mock_nep_files(virial_train, [a.get_stress() for a in atoms_train], 6)

    train, test = read_structures(tmpdir)
    for read_train, train in zip(train, atoms_train):
        assert np.allclose(
            read_train.info['energy_predicted'], train.get_potential_energy(), atol=1e-5
        )
        assert np.allclose(
            read_train.info['virial_predicted'], train.get_stress(), atol=1e-5
        )
        assert np.allclose(
            read_train.info['force_predicted'], train.get_forces(), atol=1e-5
        )

        assert np.allclose(
            read_train.info['energy_target'],
            train.get_potential_energy() - 1,
            atol=1e-5,
        )
        assert np.allclose(
            read_train.info['virial_target'], train.get_stress() - 1, atol=1e-5
        )
        assert np.allclose(
            read_train.info['force_target'], train.get_forces() - 1, atol=1e-5
        )

    for read_test, test in zip(test, atoms_test):
        assert np.allclose(
            read_test.info['energy_predicted'], test.get_potential_energy(), atol=1e-5
        )
        assert np.allclose(
            read_test.info['virial_predicted'], test.get_stress(), atol=1e-5
        )
        assert np.allclose(
            read_test.info['force_predicted'], test.get_forces(), atol=1e-5
        )

        assert np.allclose(
            read_test.info['energy_target'], test.get_potential_energy() - 1, atol=1e-5
        )
        assert np.allclose(
            read_test.info['virial_target'], test.get_stress() - 1, atol=1e-5
        )
        assert np.allclose(
            read_test.info['force_target'], test.get_forces() - 1, atol=1e-5
        )


@pytest.mark.parametrize('keyword', ['mode', 'model_type'])
def test_read_structures_polarizability(tmpdir, keyword):
    """Read polarizability_*.out file"""
    p = tmpdir.join('nep.in')
    p.write(f'{keyword} 2\n')

    polarizability = [
        full_3x3_to_voigt_6_stress(np.random.random(size=(3, 3))) for _ in range(4)
    ]
    atoms_test = [
        _get_mock_nep_atoms(polarizability=polarizability[n]) for n in range(4)
    ]
    polarizability = [
        full_3x3_to_voigt_6_stress(np.random.random(size=(3, 3))) for _ in range(7)
    ]
    atoms_train = [
        _get_mock_nep_atoms(polarizability=polarizability[n]) for n in range(7)
    ]
    polarizability_train = tmpdir.join('polarizability_train.out')
    polarizability_test = tmpdir.join('polarizability_test.out')

    write_structures(tmpdir.join('test.xyz'), atoms_test)
    write_structures(tmpdir.join('train.xyz'), atoms_train)

    _write_mock_nep_files(
        polarizability_test, [a.calc.results['polarizability'] for a in atoms_test], 6
    )
    _write_mock_nep_files(
        polarizability_train, [a.calc.results['polarizability'] for a in atoms_train], 6
    )

    train, test = read_structures(tmpdir)
    for read_train, train in zip(train, atoms_train):
        assert np.allclose(
            read_train.info['polarizability_predicted'],
            train.calc.results['polarizability'],
            atol=1e-5,
        )

        assert np.allclose(
            read_train.info['polarizability_target'],
            train.calc.results['polarizability'] - 1,
            atol=1e-5,
        )

    for read_test, test in zip(test, atoms_test):
        assert np.allclose(
            read_test.info['polarizability_predicted'],
            test.calc.results['polarizability'],
            atol=1e-5,
        )

        assert np.allclose(
            read_test.info['polarizability_target'],
            test.calc.results['polarizability'] - 1,
            atol=1e-5,
        )


def test_read_structures_polarizability_xyz_missing(tmpdir):
    """Should raise warning if train.xyz or test.xyz are missing"""
    p = tmpdir.join('nep.in')
    p.write('mode 2\n')

    polarizability = [
        full_3x3_to_voigt_6_stress(np.random.random(size=(3, 3))) for _ in range(4)
    ]
    atoms_test = [
        _get_mock_nep_atoms(polarizability=polarizability[n]) for n in range(4)
    ]
    polarizability = [
        full_3x3_to_voigt_6_stress(np.random.random(size=(3, 3))) for _ in range(7)
    ]
    atoms_train = [
        _get_mock_nep_atoms(polarizability=polarizability[n]) for n in range(7)
    ]
    polarizability_train = tmpdir.join('polarizability_train.out')
    polarizability_test = tmpdir.join('polarizability_test.out')

    _write_mock_nep_files(
        polarizability_test, [a.calc.results['polarizability'] for a in atoms_test], 6
    )
    _write_mock_nep_files(
        polarizability_train, [a.calc.results['polarizability'] for a in atoms_train], 6
    )
    with pytest.warns(UserWarning) as record:
        read_structures(tmpdir)
    assert len(record) == 2
    assert f'File {tmpdir}/train.xyz not found.' == record[0].message.args[0]
    assert f'File {tmpdir}/test.xyz not found.' == record[1].message.args[0]


def test_read_structures_dipole(tmpdir):
    """Read dipole_*.out file"""
    p = tmpdir.join('nep.in')
    p.write('mode 1\n')

    dipole_train = tmpdir.join('dipole_train.out')
    dipole_test = tmpdir.join('dipole_test.out')

    dipole = [
        full_3x3_to_voigt_6_stress(np.random.random(size=(3, 3))) for _ in range(4)
    ]
    atoms_test = [_get_mock_nep_atoms(dipole=dipole[n]) for n in range(4)]
    dipole = [
        full_3x3_to_voigt_6_stress(np.random.random(size=(3, 3))) for _ in range(7)
    ]
    atoms_train = [_get_mock_nep_atoms(dipole=dipole[n]) for n in range(7)]

    write_structures(tmpdir.join('test.xyz'), atoms_test)
    write_structures(tmpdir.join('train.xyz'), atoms_train)

    _write_mock_nep_files(dipole_test, [a.get_dipole_moment() for a in atoms_test], 6)
    _write_mock_nep_files(dipole_train, [a.get_dipole_moment() for a in atoms_train], 6)

    train, test = read_structures(tmpdir)
    for read_train, train in zip(train, atoms_train):
        assert np.allclose(
            read_train.info['dipole_predicted'], train.get_dipole_moment(), atol=1e-5
        )

        assert np.allclose(
            read_train.info['dipole_target'], train.get_dipole_moment() - 1, atol=1e-5
        )

    for read_test, test in zip(test, atoms_test):
        assert np.allclose(
            read_test.info['dipole_predicted'], test.get_dipole_moment(), atol=1e-5
        )

        assert np.allclose(
            read_test.info['dipole_target'], test.get_dipole_moment() - 1, atol=1e-5
        )


# --- read_structures
def test_read_structures_virials_3v6():
    """Read virials for GPUMD v3.6"""
    folder = './tests/example_files/nep/v3.6'
    train, test = read_structures(folder)
    assert len(train) == 2
    assert len(test) == 1

    virials_train = np.loadtxt(f'{folder}/virial_train.out').reshape((6, -1, 2)).T
    virials_test = np.loadtxt(f'{folder}/virial_test.out').reshape((6, -1, 2)).T

    total = train + test
    virials = np.concatenate((virials_train, virials_test), axis=1)
    for i, structure in enumerate(total):
        assert structure.info['energy_predicted'] is not None
        assert structure.info['energy_target'] is not None
        assert structure.info['force_predicted'].shape == (2, 3)
        assert structure.info['force_target'].shape == (2, 3)
        assert structure.info['virial_predicted'].shape == (6,)
        assert structure.info['virial_target'].shape == (6,)
        assert structure.info['stress_predicted'].shape == (6,)
        assert structure.info['stress_target'].shape == (6,)
        assert np.allclose(structure.info['virial_predicted'], virials[0, i, :])
        assert np.allclose(structure.info['virial_target'], virials[1, i, :])


def test_read_structures_virials_3v7():
    """Read virials for GPUMD v3.7"""
    folder = './tests/example_files/nep/v3.7'
    train, test = read_structures(folder)
    assert len(train) == 2
    assert len(test) == 1

    virials_train = np.loadtxt(f'{folder}/virial_train.out').reshape((-1, 12))
    virials_test = np.loadtxt(f'{folder}/virial_test.out').reshape((-1, 12))
    total = train + test
    virials = np.concatenate((virials_train, virials_test), axis=0)
    for i, structure in enumerate(total):
        assert structure.info['energy_predicted'] is not None
        assert structure.info['energy_target'] is not None
        assert structure.info['force_predicted'].shape == (2, 3)
        assert structure.info['force_target'].shape == (2, 3)
        assert structure.info['virial_predicted'].shape == (6,)
        assert structure.info['virial_target'].shape == (6,)
        assert structure.info['stress_predicted'].shape == (6,)
        assert structure.info['stress_target'].shape == (6,)
        assert np.allclose(structure.info['virial_predicted'], virials[i, :6])
        assert np.allclose(structure.info['virial_target'], virials[i, 6:])


def test_read_structures_virials_invalid_virial_shape(tmp_path):
    folder = './tests/example_files/nep/v3.7'
    for file in Path(folder).glob('*'):
        destination = tmp_path / file.name
        shutil.copy(file, destination)

    # Modify virial_train.out
    with open(tmp_path / 'virial_train.out', 'w') as f:
        f.write('0 1 2 3 4 5\n')

    with pytest.raises(ValueError) as e:
        read_structures(tmp_path)
    assert 'virial_*.out has invalid shape, (1, 3)' in str(e)


def test_read_structures_malformed_file(tmp_path):
    """File has wrong number of columns."""
    folder = './tests/example_files/nep/v3.7'
    for file in Path(folder).glob('*'):
        destination = tmp_path / file.name
        shutil.copy(file, destination)

    # Overwrite energy_train.out
    p = tmp_path / 'energy_train.out'
    p.write_text('1 2 3')  # should have 2, 6 or 12 columns
    with pytest.raises(ValueError) as e:
        read_structures(tmp_path)
    assert f'Malformed file: {str(p)}' in str(e)


def test_read_structures_missing_direcotry():
    with pytest.raises(ValueError) as e:
        read_structures('/lmao')
    assert 'Directory /lmao does not exist' in str(e)


def test_read_data_file_missing_direcotry():
    """
    Ideally we shouldn't test private functions explicitly,
    but this case cannot happen when simple calling
    read_structures, since the exact same thing is checked
    in read_structures.
    """
    with pytest.raises(ValueError) as e:
        _read_data_file('/lmao', 'hej.txt')
    assert 'Directory /lmao/hej.txt does not exist' in str(e)
