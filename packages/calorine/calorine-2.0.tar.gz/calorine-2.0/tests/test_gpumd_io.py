import tempfile

import numpy as np
import pytest
from ase import Atoms
from ase.build import bulk
from ase.io import read, write
from calorine.gpumd import (read_thermo,
                            read_kappa, read_hac,
                            read_xyz, write_xyz)


# --- read_kappa ---
def test_read_kappa():
    """Reads a kappa.out file"""
    kappa = read_kappa('tests/example_files/kappa.out')
    columns_check = kappa.columns == ['kx_in', 'kx_out', 'ky_in', 'ky_out',
                                      'kz_tot', 'kx_tot', 'ky_tot']
    assert columns_check.all()
    assert isinstance(kappa.index[0], int)
    assert isinstance(kappa['kx_in'][0], np.float64)
    assert kappa.index[0] == 0


def test_read_kappa_single_row(tmpdir):
    """Reads a single row kappa.out file"""
    p = tmpdir.join('kappa.out')
    p.write('0 1 2 3 4\n')
    kappa = read_kappa(str(p))
    columns_check = kappa.columns == ['kx_in', 'kx_out', 'ky_in', 'ky_out',
                                      'kz_tot', 'kx_tot', 'ky_tot']
    assert columns_check.all()
    assert isinstance(kappa.index[0], int)
    assert isinstance(kappa['kx_in'][0], np.float64)
    assert kappa.index[0] == 0


def test_read_kappa_nan():
    """Reads a kappa.out file filed with nans. Should this raise a warning?"""
    kappa = read_kappa('tests/example_files/kappa_nan.out')
    columns_check = kappa.columns == ['kx_in', 'kx_out', 'ky_in', 'ky_out',
                                      'kz_tot', 'kx_tot', 'ky_tot']
    assert columns_check.all()
    assert isinstance(kappa.index[0], int)
    assert isinstance(kappa['kx_in'][0], np.float64)
    assert kappa.index[0] == 0


def test_read_kappa_malformed_file(tmpdir):
    """Tries to read a malformed kappa.out file"""
    p = tmpdir.join('kappa_invalid.out')
    p.write('0 0 0 0 0 0 0 0 0 0 \n')
    with pytest.raises(ValueError) as e:
        read_kappa(str(p))
    assert 'Input file contains 10 data columns. Expected 5 columns.' in str(e)


# --- read_hac ---
def test_read_hac():
    """Reads a hac.out file"""
    hac = read_hac('tests/example_files/hac.out')
    columns_check = hac.columns == ['time', 'kx_out', 'ky_out',
                                    'kz_tot', 'kx_tot', 'ky_tot']
    assert columns_check.all()
    assert isinstance(hac.index[0], int)
    assert isinstance(hac['time'][0], np.float64)
    assert hac.index[0] == 0


def test_read_hac_single_row(tmpdir):
    """Reads a single row hac.out file"""
    p = tmpdir.join('hac.out')
    p.write('0 1 2 3 4 5 6 7 8 9 10\n')
    hac = read_hac(str(p))
    columns_check = hac.columns == ['time', 'kx_out', 'ky_out',
                                    'kz_tot', 'kx_tot', 'ky_tot']
    assert columns_check.all()
    assert isinstance(hac.index[0], int)
    assert isinstance(hac['time'][0], np.float64)
    assert hac.index[0] == 0


def test_read_hac_nan():
    """Reads a hac.out file filed with nans. Should this raise a warning?"""
    hac = read_hac('tests/example_files/hac_nan.out')
    columns_check = hac.columns == ['time', 'kx_out', 'ky_out',
                                    'kz_tot', 'kx_tot', 'ky_tot']
    assert columns_check.all()
    assert isinstance(hac.index[0], int)
    assert isinstance(hac['time'][0], np.float64)
    assert hac.index[0] == 0


def test_read_hac_malformed_file(tmpdir):
    """Tries to read a malformed hac.out file"""
    p = tmpdir.join('hac_invalid.out')
    p.write('0 0 0 \n')
    with pytest.raises(ValueError) as e:
        read_hac(str(p))
    assert 'Input file contains 3 data columns. Expected 11 columns.' in str(e)


# --- read_thermo ---
def test_read_thermo_orthorhombic():
    """Reads a thermo.out file with an orthorhombic structure"""
    thermo = read_thermo('tests/example_files/thermo_ortho_v3.2.out')
    columns_check = thermo.columns == ['temperature', 'kinetic_energy', 'potential_energy',
                                       'stress_xx', 'stress_yy', 'stress_zz',
                                       'cell_xx', 'cell_yy', 'cell_zz']
    assert columns_check.all()


def test_read_thermo_triclinic():
    """Reads a thermo.out file with an triclinic structure"""
    thermo = read_thermo('tests/example_files/thermo_tri_v3.2.out')
    columns_check = thermo.columns == ['temperature', 'kinetic_energy', 'potential_energy',
                                       'stress_xx', 'stress_yy', 'stress_zz',
                                       'cell_xx', 'cell_xy', 'cell_xz',
                                       'cell_yx', 'cell_yy', 'cell_yz',
                                       'cell_zx', 'cell_zy', 'cell_zz'
                                       ]
    assert columns_check.all()


@pytest.mark.parametrize('test_input',
                         [
                             # 9 columns --> orthorhombic cell pre GPUMD v3.3.1
                             (['temperature', 'kinetic_energy', 'potential_energy',
                               'stress_xx', 'stress_yy', 'stress_zz',
                               'cell_xx', 'cell_yy', 'cell_zz']),
                             # 15 columns --> triclinc cell pre GPUMD v3.3.1
                             (['temperature', 'kinetic_energy', 'potential_energy',
                               'stress_xx', 'stress_yy', 'stress_zz',
                               'cell_xx', 'cell_xy', 'cell_xz',
                               'cell_yx', 'cell_yy', 'cell_yz',
                               'cell_zx', 'cell_zy', 'cell_zz']),
                             # 12 columns --> orthorhombic cell GPUMD v3.3.1 forward
                             (['temperature', 'kinetic_energy', 'potential_energy',
                               'stress_xx', 'stress_yy', 'stress_zz',
                               'stress_yz', 'stress_xz', 'stress_xy',
                               'cell_xx', 'cell_yy', 'cell_zz']),
                             # 18 columns --> triclinic cell GPUMD v3.3.1 forward
                             (['temperature', 'kinetic_energy', 'potential_energy',
                               'stress_xx', 'stress_yy', 'stress_zz',
                               'stress_yz', 'stress_xz', 'stress_xy',
                               'cell_xx', 'cell_xy', 'cell_xz',
                               'cell_yx', 'cell_yy', 'cell_yz',
                               'cell_zx', 'cell_zy', 'cell_zz'])
                         ])
def test_read_thermo_pass(test_input):
    """Reads dummy thermo.out files and checks that the correct columns are being returned"""
    s = ' '.join(map(str, range(len(test_input)))) + '\n'
    tmpfile = tempfile.NamedTemporaryFile()
    with open(tmpfile.name, 'w') as f:
        for _ in range(10):
            f.write(s)
    with open(tmpfile.name, 'r') as f:
        thermo = read_thermo(f.name)
    tmpfile.close()
    columns_check = thermo.columns == test_input
    assert columns_check.all()


def test_read_thermo_fail():
    """Checks that ValueError is raised if the number of columns is incorrect"""
    for n in range(1, 20):
        s = ' '.join(map(str, range(n))) + '\n'
        tmpfile = tempfile.NamedTemporaryFile()
        with open(tmpfile.name, 'w') as f:
            for _ in range(10):
                f.write(s)
        with open(tmpfile.name, 'r') as f:
            if n in [9, 15, 12, 18]:
                _ = read_thermo(f.name)
            else:
                with pytest.raises(ValueError) as e:
                    read_thermo(f.name)
                assert 'Expected 9, 12, 15 or 18 columns.' in str(e)
        tmpfile.close()


def test_read_thermo_malformed_file(tmpdir):
    """Tries to read a malformed thermo.out file"""
    p = tmpdir.join('thermo_invalid.out')
    p.write('NaN NaN NaN NaN NaN NaN\n')
    with pytest.raises(ValueError) as e:
        read_thermo(str(p))
    assert 'Input file contains 6 data columns. Expected 9, 12, 15 or 18 columns.' in str(e)


# --- read_xyz and write_xyz ---
def test_write_read_xyz(tmpdir):
    """Writes and reads xyz files"""

    f = str(tmpdir.join('atoms.xyz'))
    structure_orig = bulk('C').repeat(3)
    write_xyz(f, structure_orig)
    structure_read = read_xyz(f)
    assert len(structure_orig) == len(structure_read)
    assert np.allclose(structure_orig.cell, structure_read.cell)
    assert np.allclose(structure_orig.positions, structure_read.positions)

    write_xyz(f, structure_orig)
    structure_read = read_xyz(f)
    velocities = structure_read.get_velocities()
    assert np.max(np.abs(velocities)) < 1e-6


def test_write_read_xyz_has_velocity(tmpdir):
    """Writes and reads an orthorhombic structure with velocity"""
    f = str(tmpdir.join('atoms.xyz'))
    structure = Atoms('CCC', positions=[(0, 0, 0), (0, 0, 1.1), (0, 0, 2.2)], cell=[1, 2, 3])
    vel = [[0, 0, 100], [0, 0, 150], [0, 0, 200]]
    structure.set_velocities(vel)
    write_xyz(f, structure)
    structure_read = read_xyz(f)
    velocities = structure_read.get_velocities()
    assert np.allclose(velocities, vel)


# def test_write_read_xyz_groupings(tmpdir):
    """Writes and reads a structure with groups"""
    f = str(tmpdir.join('atoms.xyz'))
    structure = Atoms('CCCC',
                      positions=[(0, 0, 0), (0, 0, 1.1), (0, 0, 2.2), (0, 0, 3.3)],
                      cell=[1, 2, 3])
    write_xyz(f, structure, groupings=[[[0, 1], [2, 3]], [[0], [1, 2, 3]]])
    structure_read = read_xyz(f)
    assert len(structure_read.get_array('group')[0]) == 2


def test_write_xyz_invalid_groupings(tmpdir):
    """Tries to write with invalid groups"""
    f = tmpdir.join('atoms.xyz')
    structure = Atoms('CCC', positions=[(0, 0, 0), (0, 0, 1.1), (0, 0, 2.2)], cell=[1, 2, 3])
    with pytest.raises(ValueError) as e:
        # Too many groupings
        write_xyz(f, structure, groupings=[[[0, 1], [2]], [
                  [0, 1], [2]], [[0, 1], [2]], [[0, 1], [2]]])
    assert 'There can be no more than 3 grouping methods!' in str(e)
    with pytest.raises(ValueError) as e:
        # Number of atoms do not add up to the total
        write_xyz(f, structure, groupings=[[[0, 1], [1, 2]]])
    assert 'method 0 are not compatible with the input structure!' in str(e)


# --- Check dump.xyz ---
# Not a unit test, but a good FYI test for our sake
def test_ase_correctly_parses_dump(tmpdir):
    """Check that ASE can correctly read dump files"""
    dump_file = 'tests/example_files/md_no_velocities_or_forces/dump.xyz'
    snapshots = read(dump_file, index=':')
    traj = tmpdir.join('lmao.traj')
    write(f'{traj}', snapshots)  # Make sure that writing works without crashing
    assert all(snapshots[-1][-1].position == [3.10105816, 2.94360168, 2.68268773])


def test_ase_correctly_parses_dump_forces_and_velocities(tmpdir):
    """Check that ASE can correctly read dump files with forces and velocities"""
    dump_file = 'tests/example_files/md_velocities_and_forces/dump.xyz'
    snapshots = read(dump_file, index=':')
    traj = tmpdir.join('lmao.traj')
    write(f'{traj}', snapshots)  # Make sure that writing works without crashing
    assert all(snapshots[-1][-1].position == [3.24197501, 2.84584855, 2.89100032])
    assert all(snapshots[-1].get_array('vel')[-1] == [-0.00033243, 0.00061451, 0.00044743])
    assert all(snapshots[-1].get_array('forces')[-1] == [-0.96089202, -0.01649800, -0.11494368])
