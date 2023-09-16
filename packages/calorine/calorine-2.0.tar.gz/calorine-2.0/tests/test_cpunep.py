import contextlib
from pathlib import Path

import numpy as np
import pytest
from ase import Atoms
from ase.build import bulk
from ase.db import connect
from ase.io import read
from ase.stress import full_3x3_to_voigt_6_stress

from calorine.calculators import CPUNEP, GPUNEP
from calorine.nep import get_dipole_gradient

# Use same volume as in PbTe_2atom.in, C_2atom.in etc.
vacuum_cell = ([100, 0, 0], [0, 100, 0], [0, 0, 100])


@pytest.fixture
def PbTe():
    return Atoms('TePb', positions=[(0, 0, 0), (0, 0.0, 1.1)], cell=vacuum_cell)


@pytest.fixture
def C():
    return Atoms('C', positions=[(0, 0, 0)], cell=vacuum_cell)


@pytest.fixture
def CC():
    return Atoms('CC', positions=[(0, 0, 0), (0, 0.0, 1.1)], cell=vacuum_cell)


@pytest.fixture
def CO():
    return Atoms('CO', positions=[(0, 0, 0), (0, 0.0, 1.1)], cell=vacuum_cell)


@pytest.fixture
def CON():
    return Atoms(
        'CON', positions=[(0, 0, 0), (0, 0.0, 1.1), (0, 0.0, 2.2)], cell=vacuum_cell
    )


@pytest.fixture
def PbTeBulk():
    PbTeBulk = bulk('PbTe', crystalstructure='rocksalt', a=4)
    PbTeBulk[0].position += np.array([0.03, 0.02, 0])
    return PbTeBulk


@pytest.fixture
def NEP3File():
    nep3 = 'tests/nep_models/nep3_v3.3.1_PbTe_Fan22.txt'
    return nep3


@pytest.fixture
def NEP3CPUNEP(NEP3File):
    calc = CPUNEP(NEP3File)
    return calc


@pytest.fixture
def DipoleFile():
    return 'tests/nep_models/nep4_dipole_Christian.txt'


@pytest.fixture
def DipoleCPUNEP(DipoleFile):
    calc = CPUNEP(DipoleFile, debug=True)
    return calc


def get_expected_forces(path):
    return np.loadtxt(path)


def get_expected_stress(path, voigt=True):
    volume = vacuum_cell[0][0] * vacuum_cell[1][1] * vacuum_cell[2][2]
    stress = (np.sum(-np.loadtxt(path), axis=0) / volume).reshape((3, 3))
    if voigt:
        return full_3x3_to_voigt_6_stress(stress)
    return stress


# --- get_potential_forces_and_virials ---
def test_get_potential_forces_and_stress_NEP3(PbTe):
    """NEP3 model supplied. Compares results to output from `nep_cpu`"""
    nep3 = 'tests/nep_models/nep3_v3.3.1_PbTe_Fan22.txt'
    calc = CPUNEP(nep3)
    PbTe.calc = calc
    energy = PbTe.get_potential_energy()
    forces = PbTe.get_forces()
    stress = PbTe.get_stress()

    expected_forces = get_expected_forces(
        'tests/example_output/nep3_v3.3.1_PbTe_Fan22_PbTe_2atom_force.out'
    )
    expected_stress = get_expected_stress(
        'tests/example_output/nep3_v3.3.1_PbTe_Fan22_PbTe_2atom_virial.out'
    )

    assert energy.shape == ()
    assert forces.shape == (2, 3)
    assert stress.shape == (6,)
    assert np.allclose(forces[0, :], -forces[1, :], atol=1e-12, rtol=0)  # Newton III
    assert np.allclose(forces, expected_forces, atol=1e-12, rtol=0)
    assert np.allclose(stress, expected_stress, atol=1e-12, rtol=0)


def test_get_potential_forces_and_stress_set_atoms_constructor(PbTe):
    """Set atoms directly when creating the calculator"""
    nep3 = 'tests/nep_models/nep3_v3.3.1_PbTe_Fan22.txt'
    CPUNEP(nep3, atoms=PbTe)
    energy = PbTe.get_potential_energy()
    forces = PbTe.get_forces()
    stress = PbTe.get_stress()

    expected_forces = get_expected_forces(
        'tests/example_output/nep3_v3.3.1_PbTe_Fan22_PbTe_2atom_force.out'
    )
    expected_stress = get_expected_stress(
        'tests/example_output/nep3_v3.3.1_PbTe_Fan22_PbTe_2atom_virial.out'
    )

    assert energy.shape == ()
    assert forces.shape == (2, 3)
    assert stress.shape == (6,)
    assert np.allclose(forces[0, :], -forces[1, :], atol=1e-12, rtol=0)  # Newton III
    assert np.allclose(forces, expected_forces, atol=1e-12, rtol=0)
    assert np.allclose(stress, expected_stress, atol=1e-12, rtol=0)


def test_get_potential_forces_and_stress_set_atoms_calculate(PbTe):
    """Set atoms directly when calling calculate on the calculator"""
    nep3 = 'tests/nep_models/nep3_v3.3.1_PbTe_Fan22.txt'
    calc = CPUNEP(nep3)
    calc.calculate(atoms=PbTe)
    results = calc.results
    energy = results['energy']
    forces, stress = results['forces'], results['stress']

    expected_forces = get_expected_forces(
        'tests/example_output/nep3_v3.3.1_PbTe_Fan22_PbTe_2atom_force.out'
    )
    expected_stress = get_expected_stress(
        'tests/example_output/nep3_v3.3.1_PbTe_Fan22_PbTe_2atom_virial.out', voigt=True
    )

    assert energy.shape == ()
    assert forces.shape == (2, 3)
    assert stress.shape == (6,)
    assert np.allclose(forces[0, :], -forces[1, :], atol=1e-12, rtol=0)  # Newton III
    assert np.allclose(forces, expected_forces, atol=1e-12, rtol=0)
    assert np.allclose(stress, expected_stress, atol=1e-12, rtol=0)


def test_get_potential_forces_and_stress_NEP3_debug(tmpdir, PbTe):
    """Compares result with debug flag enabled."""
    nep3 = 'tests/nep_models/nep3_v3.3.1_PbTe_Fan22.txt'
    calc = CPUNEP(nep3, debug=True)
    p = tmpdir.join('nep_out.tmp')
    with open(p, 'w') as f:
        with contextlib.redirect_stdout(f):
            with contextlib.redirect_stderr(f):
                PbTe.calc = calc
                PbTe.get_potential_energy()
                PbTe.get_forces()
                PbTe.get_stress()
    with open(p, 'r') as f:
        lines = p.readlines()
        assert lines[0] == 'Use the NEP3 potential with 2 atom types.\n'
        assert len(lines) == 16


def test_get_tress_non_voigt_NEP3(PbTe):
    """NEP3 model supplied. Compares results to output from `nep_cpu`"""
    nep3 = 'tests/nep_models/nep3_v3.3.1_PbTe_Fan22.txt'
    calc = CPUNEP(nep3)
    PbTe.calc = calc
    stress = PbTe.get_stress(voigt=False)
    expected_stress = get_expected_stress(
        'tests/example_output/nep3_v3.3.1_PbTe_Fan22_PbTe_2atom_virial.out', voigt=False
    )

    assert stress.shape == (3, 3)
    assert np.allclose(stress, expected_stress, atol=1e-12, rtol=0)


def test_get_potential_forces_and_stress_dummy_NEP2(CO):
    """Dummy NEP2 model supplied. Compares results to output from `nep_cpu` for another system"""
    nep2 = 'tests/nep_models/CO_NEP2_dummy.txt'
    calc = CPUNEP(nep2)
    CO.calc = calc
    energy = CO.get_potential_energy()
    forces = CO.get_forces()
    stress = CO.get_stress()

    expected_forces = get_expected_forces(
        'tests/example_output/CO_NEP2_dummy_CO_2atom_force.out'
    )
    expected_stress = get_expected_stress(
        'tests/example_output/CO_NEP2_dummy_CO_2atom_virial.out'
    )

    assert energy.shape == ()
    assert forces.shape == (2, 3)
    assert stress.shape == (6,)
    assert np.allclose(forces[0, :], -forces[1, :], atol=1e-12, rtol=0)  # Newton III
    assert np.allclose(forces, expected_forces, atol=1e-12, rtol=0)
    assert np.allclose(stress, expected_stress, atol=1e-12, rtol=0)


def test_get_potential_forces_and_stress_several_different_species(CON):
    """Check that forces and stress are correct for a CON system.
    Note that these forces/stress should be exactly zero for this system
    since the NEP2 dummy potential treats all atom species as identical atm."""
    nep2 = 'tests/nep_models/CON_NEP2_dummy.txt'
    calc = CPUNEP(nep2)
    CON.calc = calc
    energy = CON.get_potential_energy()
    forces = CON.get_forces()
    stress = CON.get_stress()

    expected_forces = get_expected_forces(
        'tests/example_output/CON_NEP2_dummy_CON_3atom_force.out'
    )
    expected_stress = get_expected_stress(
        'tests/example_output/CON_NEP2_dummy_CON_3atom_virial.out'
    )

    assert energy.shape == ()
    assert forces.shape == (3, 3)
    assert stress.shape == (6,)
    assert np.allclose(forces[0, :], -forces[1, :], atol=1e-12, rtol=0)  # Newton III
    assert np.allclose(forces, expected_forces, atol=1e-12, rtol=0)
    assert np.allclose(forces, np.zeros((3, 3)), atol=1e-12, rtol=0)
    assert np.allclose(stress, expected_stress, atol=1e-12, rtol=0)
    assert np.allclose(stress, np.zeros((6,)), atol=1e-12, rtol=0)


def test_get_potential_forces_and_stress_dummy_NEP2_independent_of_species(PbTe, CO):
    """Dummy NEP2 energies, forces and stress should be independent of atom species"""
    nep2 = 'tests/nep_models/PbTe_NEP2_dummy.txt'
    calc = CPUNEP(nep2)
    PbTe.calc = calc
    PbTe_energy = PbTe.get_potential_energy()
    PbTe_forces = PbTe.get_forces()
    PbTe_stress = PbTe.get_stress()

    nep2 = 'tests/nep_models/CO_NEP2_dummy.txt'
    calc = CPUNEP(nep2)
    CO.calc = calc
    CO_energy = CO.get_potential_energy()
    CO_forces = CO.get_forces()
    CO_stress = CO.get_stress()

    expected_forces_CO = get_expected_forces(
        'tests/example_output/CO_NEP2_dummy_CO_2atom_force.out'
    )
    expected_stress_CO = get_expected_stress(
        'tests/example_output/CO_NEP2_dummy_CO_2atom_virial.out'
    )

    assert np.allclose(PbTe_energy, CO_energy, atol=1e-12, rtol=0)
    assert np.allclose(PbTe_forces, CO_forces, atol=1e-12, rtol=0)
    assert np.allclose(PbTe_stress, CO_stress, atol=1e-12, rtol=0)
    assert np.allclose(CO_forces, expected_forces_CO, atol=1e-12, rtol=0)
    assert np.allclose(CO_stress, expected_stress_CO, atol=1e-12, rtol=0)


def test_get_potential_forces_and_stress_update_positions(PbTe):
    """Update the positions and make sure that the energies, forces and stress are also updated"""
    nep3 = 'tests/nep_models/nep3_v3.3.1_PbTe_Fan22.txt'
    calc = CPUNEP(nep3)

    copy = PbTe.copy()
    copy.calc = calc
    energy_initial = copy.get_potential_energy()
    forces_initial = copy.get_forces()
    stress_initial = copy.get_stress()

    # Move atoms slightly
    copy.set_positions([[0, 0, 0], [0, 0, 2.2]])
    energy_after = copy.get_potential_energy()
    forces_after = copy.get_forces()
    stress_after = copy.get_stress()

    diff_energy = np.abs(energy_after - energy_initial)
    diff_force = forces_initial - forces_after
    diff_stress = stress_initial - stress_after

    assert np.isclose(diff_energy, 1.80751674, atol=1e-12, rtol=1e-6)
    assert np.allclose(
        diff_force, [[0, 0, 4.65672972], [0, 0, -4.65672972]], atol=1e-12, rtol=1e-6
    )
    assert np.allclose(
        diff_stress, [0, 0, 7.13057884e-06, 0, 0, 0], atol=1e-12, rtol=1e-6
    )


def test_get_potential_forces_and_stress_update_cell(PbTe):
    """Update the cell and make sure that the energies, forces and stress are still the same"""
    nep3 = 'tests/nep_models/nep3_v3.3.1_PbTe_Fan22.txt'
    calc = CPUNEP(nep3)

    copy = PbTe.copy()
    copy.calc = calc
    energy_initial = copy.get_potential_energy()
    forces_initial = copy.get_forces()
    stress_initial = copy.get_stress()

    # Change box
    new_cell = ([20, 0, 0], [0, 20, 0], [0, 0, 20])
    copy.set_cell(new_cell, scale_atoms=False)
    volume_factor = vacuum_cell[0][0] ** 3 / (new_cell[0][0] ** 3)
    copy.center()

    energy_after = copy.get_potential_energy()
    forces_after = copy.get_forces()
    stress_after = copy.get_stress()

    assert np.isclose(energy_initial, energy_after, atol=1e-12, rtol=1e-6)
    assert np.allclose(forces_initial, forces_after, atol=1e-12, rtol=1e-6)
    assert np.allclose(
        stress_initial, stress_after / volume_factor, atol=1e-12, rtol=1e-6
    )


def test_get_potential_forces_and_stress_update_numbers(PbTe):
    """Update the atom numbers (species) and make sure that the
    energies, forces and stress are also updated.
    """
    nep3 = 'tests/nep_models/nep3_v3.3.1_PbTe_Fan22.txt'
    calc = CPUNEP(nep3)

    copy = PbTe.copy()
    copy.calc = calc
    energy_initial = copy.get_potential_energy()
    forces_initial = copy.get_forces()
    stress_initial = copy.get_stress()

    # Change atomic numbers
    copy.set_atomic_numbers([82, 82])  # Pb_2

    energy_after = copy.get_potential_energy()
    forces_after = copy.get_forces()
    stress_after = copy.get_stress()

    diff_energy = np.abs(energy_after - energy_initial)
    diff_force = forces_initial - forces_after
    diff_stress = stress_initial - stress_after
    assert np.isclose(diff_energy, 1.86577361, atol=1e-12, rtol=1e-6)
    assert np.allclose(
        diff_force, [[0, 0, 1.07038059], [0, 0, -1.07038059]], atol=1e-12, rtol=1e-6
    )
    assert np.allclose(
        diff_stress, [0, 0, 1.17741865e-06, 0, 0, 0], atol=1e-12, rtol=1e-6
    )


def test_reset_calculator_on_atoms_change(PbTe):
    """Reset the calculator when changing the system."""
    nep3 = 'tests/nep_models/nep3_v3.3.1_PbTe_Fan22.txt'
    calc = CPUNEP(nep3)

    copy = PbTe.copy()
    copy.calc = calc
    energy_initial = copy.get_potential_energy()
    forces_initial = copy.get_forces()
    stress_initial = copy.get_stress()

    # Copy system
    atoms_copy = copy.copy()
    original_cell = copy.cell.copy()
    atoms_copy.calc = calc

    assert calc.results == {}
    assert calc.nepy is None

    # Scale cell
    atoms_copy.set_cell(1.1 * original_cell, scale_atoms=True)
    energy_after = atoms_copy.get_potential_energy()
    forces_after = atoms_copy.get_forces()
    stress_after = atoms_copy.get_stress()

    diff_energy = np.abs(energy_after - energy_initial)
    diff_force = forces_initial - forces_after
    diff_stress = stress_initial - stress_after
    assert np.isclose(diff_energy, 0.28572432, atol=1e-12, rtol=1e-6)
    assert np.allclose(
        diff_force, [[0, 0, 0.27278336], [0, 0, -0.27278336]], atol=1e-12, rtol=1e-6
    )
    assert np.allclose(
        diff_stress, [0, 0, 7.88470474e-07, 0, 0, 0], atol=1e-12, rtol=1e-6
    )


def test_get_potential_posix_path(PbTe):
    """Should properly cast posix path to str"""
    nep3 = Path('tests/nep_models/nep3_v3.3.1_PbTe_Fan22.txt')
    calc = CPUNEP(nep3)
    PbTe.calc = calc
    energy = PbTe.get_potential_energy()
    assert np.isclose(energy, -4.909041589570421, atol=1e-12, rtol=1e-6)


def test_get_potential_and_forces_no_cell():
    """Should raise error if no cell is supplied"""
    nep3 = 'tests/nep_models/nep3_v3.3.1_PbTe_Fan22.txt'
    calc = CPUNEP(nep3)
    atoms = Atoms('Pb', positions=[(0, 0, 0)])
    atoms.calc = calc
    with pytest.raises(ValueError) as e:
        atoms.get_potential_energy()
    assert 'Atoms must have a defined cell.' in str(e)


def test_get_potential_and_forces_no_potential():
    """Tries to get potentials and forces without specifying potential"""
    with pytest.raises(FileNotFoundError) as e:
        CPUNEP('nep.txt')
    assert 'nep.txt does not exist.' in str(e)


def test_get_potential_and_forces_no_atoms():
    """Tries to get potential and forces without specifying atoms"""
    nep3 = 'tests/nep_models/nep3_v3.3.1_PbTe_Fan22.txt'
    calc = CPUNEP(nep3)
    with pytest.raises(ValueError) as e:
        calc.calculate()
    assert 'Atoms must be defined to get energies and forces.' in str(e)


def test_CPU_GPU_equivalent(PbTe):
    """Assert that the CPU and GPU implementation are equivalent"""
    nep3 = 'tests/nep_models/nep3_v3.3.1_PbTe_Fan22.txt'
    # CPU
    PbTe.calc = CPUNEP(nep3)
    cpu_energy = PbTe.get_potential_energy()
    cpu_forces = PbTe.get_forces()
    cpu_stress = PbTe.get_stress()
    # GPU
    PbTe.calc = GPUNEP(nep3)
    gpu_energy = PbTe.get_potential_energy()
    gpu_forces = PbTe.get_forces()
    gpu_stress = PbTe.get_stress()
    assert np.isclose(cpu_energy, gpu_energy, atol=1e-12, rtol=1e-5)
    # GPUMD forces are in single precision, meaning errors can add up to 1e-6
    assert np.allclose(cpu_forces, gpu_forces, atol=1e-12, rtol=1e-5)
    assert np.allclose(cpu_stress, gpu_stress, atol=1e-12, rtol=1e-5)


def test_CPU_GPU_equivalent_bulk(PbTeBulk):
    """Assert that the CPU and GPU implementation are equivalent for a bulk PbTE system"""
    nep3 = 'tests/nep_models/nep3_v3.3.1_PbTe_Fan22.txt'
    print(PbTeBulk.get_volume())
    # CPU
    PbTeBulk.calc = CPUNEP(nep3)
    cpu_energy = PbTeBulk.get_potential_energy()
    cpu_forces = PbTeBulk.get_forces()
    cpu_stress = PbTeBulk.get_stress(voigt=False)
    # GPU
    PbTeBulk.calc = GPUNEP(nep3)
    gpu_energy = PbTeBulk.get_potential_energy()
    gpu_forces = PbTeBulk.get_forces()
    gpu_stress = PbTeBulk.get_stress(voigt=False)
    assert np.isclose(cpu_energy, gpu_energy, atol=1e-5, rtol=1e-5)
    # GPUMD forces are in single precision, meaning errors can add up to 1e-6
    assert np.allclose(cpu_forces, gpu_forces, atol=1e-5, rtol=1e-5)
    assert np.allclose(cpu_stress, gpu_stress, atol=1e-5, rtol=1e-5)


def test_cpunep_readwrite_dict(NEP3CPUNEP):
    dict = NEP3CPUNEP.todict()
    assert dict['model_filename'] == 'tests/nep_models/nep3_v3.3.1_PbTe_Fan22.txt'
    restored_calc = CPUNEP(**dict)
    all_keys = dict.keys()
    assert all(
        [getattr(restored_calc, key) == getattr(NEP3CPUNEP, key) for key in all_keys]
    )


def test_cpunep_tostr(NEP3CPUNEP):
    s = str(NEP3CPUNEP)
    assert 'tests/nep_models/nep3_v3.3.1_PbTe_Fan22.txt' in s


def test_cpunep_readwrite_db(tmpdir, NEP3CPUNEP, PbTeBulk):
    PbTeBulk.calc = NEP3CPUNEP
    with connect(f'{tmpdir}/db.db') as db:
        db.write(PbTeBulk)
    atoms = None
    with connect(f'{tmpdir}/db.db') as db:
        for row in db.select():
            atoms = row.toatoms()
            atoms.calc = CPUNEP(**row.calculator_parameters)
    assert atoms == PbTeBulk
    assert atoms.calc is not None
    all_keys = ['model_filename']
    assert all(
        [getattr(atoms.calc, key) == getattr(NEP3CPUNEP, key) for key in all_keys]
    )


# ---- get_dipole() ----
def test_get_dipole(DipoleCPUNEP):
    """Compares results to output from DFT."""
    structure = read('tests/example_files/dipole/test.xyz')
    structure.calc = DipoleCPUNEP

    dipole = structure.get_dipole_moment()
    dft_dipole = structure.info['dipole']
    delta = dipole - dft_dipole

    assert dipole.shape == (3,)
    assert np.allclose(
        [-0.07468218, -0.03891397, -0.11160894], delta, atol=1e-12, rtol=1e-5
    )


# ---- get_dipole_gradient ----
def test_get_dipole_gradient(DipoleCPUNEP, DipoleFile):
    """
    Dipole gradients are computed using finite differences.
    Compare calculator to Python implementation.
    """
    structure = read('tests/example_files/dipole/test.xyz')
    N = len(structure)

    # Get reference values with Python implementation
    gradient_forward_python = get_dipole_gradient(
        structure,
        model_filename=DipoleFile,
        displacement=0.001,
        backend='python',
        method='forward difference',
        charge=2.0,
    )

    gradient_central_python = get_dipole_gradient(
        structure,
        model_filename=DipoleFile,
        displacement=0.001,
        backend='python',
        method='central difference',
        charge=2.0,
    )

    assert gradient_forward_python.shape == (N, 3, 3)
    assert gradient_central_python.shape == (N, 3, 3)
    assert not np.allclose(
        gradient_central_python, gradient_forward_python, atol=1e-12, rtol=1e-6
    )
    assert not np.allclose(gradient_forward_python, 0, atol=1e-12, rtol=1e-6)

    # Test CPUNEP implementation
    DipoleCPUNEP.atoms = structure
    gradient_forward_cpp = DipoleCPUNEP.get_dipole_gradient(
        displacement=0.001, method='forward difference', charge=2.0
    )

    gradient_central_cpp = DipoleCPUNEP.get_dipole_gradient(
        displacement=0.001, method='central difference', charge=2.0
    )

    assert gradient_forward_cpp.shape == (N, 3, 3)
    assert gradient_central_cpp.shape == (N, 3, 3)
    assert np.allclose(
        gradient_forward_cpp, gradient_forward_python, atol=1e-12, rtol=1e-6
    )
    assert np.allclose(
        gradient_central_cpp, gradient_central_python, atol=1e-12, rtol=1e-6
    )


def test_get_dipole_gradient_second_order(DipoleCPUNEP, DipoleFile):
    """Compare second order central difference to first order"""
    structure = read('tests/example_files/dipole/test.xyz')
    N = len(structure)

    gradient_second_python = get_dipole_gradient(
        structure,
        model_filename=DipoleFile,
        displacement=1e-2,
        backend='python',
        method='second order central difference',
        charge=2.0,
    )

    DipoleCPUNEP.atoms = structure
    gradient_first_cpp = DipoleCPUNEP.get_dipole_gradient(
        displacement=1e-2, method='central difference', charge=2.0
    )

    gradient_second_cpp = DipoleCPUNEP.get_dipole_gradient(
        displacement=1e-2, method='second order central difference', charge=2.0
    )

    assert gradient_first_cpp.shape == (N, 3, 3)
    assert gradient_second_cpp.shape == (N, 3, 3)
    # Second order should give somewhat the same results as first order
    # I.e. on the same order.
    assert np.allclose(gradient_first_cpp, gradient_second_cpp, atol=1e-1, rtol=1e-1)

    # Should be numerically exact with Python
    assert np.allclose(
        gradient_second_cpp, gradient_second_python, atol=1e-12, rtol=1e-6
    )


def test_get_dipole_gradient_defaults(DipoleCPUNEP, DipoleFile):
    """Make sure that the results with default kwargs match expected results."""
    structure = read('tests/example_files/dipole/test.xyz')

    DipoleCPUNEP.atoms = structure
    gradient_default = DipoleCPUNEP.get_dipole_gradient()

    DipoleCPUNEP.atoms = structure
    gradient_central = DipoleCPUNEP.get_dipole_gradient(
        displacement=0.01, method='central difference'
    )

    assert np.allclose(gradient_default, gradient_central, atol=1e-12, rtol=1e-6)
    assert np.allclose(gradient_default, gradient_central, atol=1e-12, rtol=1e-6)


def test_get_dipole_gradient_numeric(DipoleCPUNEP, DipoleFile):
    """Compare gradient to manually computed, for a two atom system"""
    structure = read('tests/example_files/dipole/test.xyz')[:2]

    expected = [733.95084217, 4.56472784, 16.75684465]
    gradient_python = get_dipole_gradient(
        structure,
        model_filename=DipoleFile,
        displacement=0.01,
        backend='python',
        method='forward difference',
        charge=2.0,
    )
    gradient = gradient_python[0, 0, :]
    assert np.allclose(expected, gradient, atol=1e-12, rtol=1e-6)

    DipoleCPUNEP.atoms = structure
    gradient_cpp = DipoleCPUNEP.get_dipole_gradient(
        displacement=0.01, method='forward difference', charge=2.0
    )
    gradient = gradient_cpp[0, 0, :]
    assert np.allclose(expected, gradient, atol=1e-12, rtol=1e-6)


def test_get_dipole_gradient_numeric_without_correction(DipoleCPUNEP, DipoleFile):
    """Compare gradient to manually computed, for a two atom system"""
    structure = read('tests/example_files/dipole/test.xyz')[:2]

    expected = [733.14383155, 4.56472784, 16.75684465]
    gradient_python = get_dipole_gradient(
        structure,
        model_filename=DipoleFile,
        displacement=0.01,
        backend='python',
        method='forward difference',
        charge=0.0,
    )
    gradient = gradient_python[0, 0, :]
    assert np.allclose(expected, gradient, atol=1e-12, rtol=1e-6)

    DipoleCPUNEP.atoms = structure
    gradient_cpp = DipoleCPUNEP.get_dipole_gradient(
        displacement=0.01, method='forward difference', charge=0.0
    )
    gradient = gradient_cpp[0, 0, :]
    assert np.allclose(expected, gradient, atol=1e-12, rtol=1e-6)


def test_get_dipole_gradient_invalid_method(DipoleCPUNEP, PbTe):
    """Tries to get dipole gradient whilst specifying an invalid method"""
    with pytest.raises(ValueError) as e:
        DipoleCPUNEP.atoms = PbTe
        DipoleCPUNEP.get_dipole_gradient(displacement=0.01, method='lmao')
    assert 'Invalid method lmao for calculating gradient' in str(e)


def test_get_dipole_gradient_invalid_displacement(DipoleCPUNEP, PbTe):
    """Tries to get dipole gradient with an invalid displacement"""
    with pytest.raises(ValueError) as e:
        DipoleCPUNEP.atoms = PbTe
        DipoleCPUNEP.get_dipole_gradient(displacement=-0.01, method='lmao')
    assert 'displacement must be > 0 Å' in str(e)


def test_get_dipole_gradient_invalid_potential(NEP3CPUNEP, PbTe):
    """Tries to get dipole gradient with a non-dipole model"""
    with pytest.raises(ValueError) as e:
        NEP3CPUNEP.atoms = PbTe
        NEP3CPUNEP.get_dipole_gradient()
    assert 'Dipole gradients are only defined for dipole NEP models.' in str(e)


# --- meta data ---
@pytest.mark.parametrize(
    'nep_file,version,species',
    [
        ('./tests/nep_models/C_NEP2_dummy.txt', 2, ['C']),
        ('./tests/nep_models/nep3_v3.2_PbTe_Fan22.txt', 3, ['Pb', 'Te']),
        ('./tests/nep_models/nep4_dipole_Christian.txt', 4, ['F', 'Si', 'C', 'H']),
    ],
)
def test_model_type_version_and_species(nep_file, version, species):
    """Check that CPUNEP has correct attributes set."""
    calc = CPUNEP(nep_file)
    assert calc.nep_version == version
    assert set(calc.supported_species) == set(species)


@pytest.mark.parametrize(
    'nep_file,atoms,raises',
    [
        ('./tests/nep_models/C_NEP2_dummy.txt', 'PbTe', True),
        ('./tests/nep_models/nep3_v3.2_PbTe_Fan22.txt', 'C', True),
        ('./tests/nep_models/C_NEP2_dummy.txt', 'CO', True),
        ('./tests/nep_models/CO_NEP2_dummy.txt', 'C', False),
    ],
)
def test_CPUNEP_invalid_species(request, nep_file, atoms, raises):
    """Check that CPUNEP throws an error if atoms contains unsupported species."""
    atoms = request.getfixturevalue(atoms)
    calc = CPUNEP(nep_file)
    if raises:
        with pytest.raises(ValueError) as e:
            atoms.calc = calc
        assert 'Structure contains species that are not supported by the NEP model.' in str(e)
    else:
        atoms.calc = calc
        species_in_atoms_object = set(np.unique(atoms.get_chemical_symbols()))
        assert species_in_atoms_object.issubset(calc.supported_species)
