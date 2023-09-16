import numpy as np
import pytest
from ase import Atoms
from ase.io import read

from calorine.nep.model import read_model
from calorine.nep.nep import (
    _clean_tmp_dir,
    _predict_dipole_batch,
    _set_dummy_energy_forces,
    get_descriptors,
    get_dipole,
    get_dipole_gradient,
    get_latent_space,
    get_polarizability,
    get_potential_forces_and_virials,
)


@pytest.fixture
def PbTe():
    return Atoms(
        'TePb',
        positions=[(0, 0, 0), (0, 0.0, 1.1)],
        cell=([100, 0, 0], [0, 100, 0], [0, 0, 100]),
    )


@pytest.fixture
def C():
    return Atoms('C', positions=[(0, 0, 0)])


@pytest.fixture
def CC():
    return Atoms('CC', positions=[(0, 0, 0), (0, 0.0, 1.1)])


@pytest.fixture
def CO():
    return Atoms('CO', positions=[(0, 0, 0), (0, 0.0, 1.1)])


@pytest.fixture
def CON():
    return Atoms('CON', positions=[(0, 0, 0), (0, 0.0, 1.1), (0, 0.0, 2.2)])


@pytest.fixture
def nep3_dipole():
    return 'tests/nep_models/nep4_dipole_Christian.txt'


@pytest.fixture
def nep3_pol():
    return 'tests/nep_models/nep3_polarizability_BaZrO3.txt'


def get_expected(path):
    """Load forces or virials from file"""
    return np.loadtxt(path)


def _load_nep_from_file(file: str) -> str:
    """Load a NEP model from file into a stringified version

    Parameters
    ----------
    file
        Path to nep.txt.

    Returns
    -------
    str
        Stringified NEP model.
    """
    with open(file, 'r') as f:
        model = f.read()
    return model


# --- get_descriptors ---
def test_get_descriptors_setup_dummy_NEP2_model(PbTe):
    """Verifies the dummy NEP model is properly formatted."""
    get_descriptors(PbTe, debug=True)
    tmp_dir = './tmp_nepy/'
    PbTe_dummy = _load_nep_from_file(f'{tmp_dir}/nep.txt')
    _clean_tmp_dir(tmp_dir)
    expected_PbTe_dummy = _load_nep_from_file('tests/nep_models/PbTe_NEP2_dummy.txt')
    assert PbTe_dummy == expected_PbTe_dummy


def test_get_descriptors_no_cell(CO):
    """Should get descriptors for atoms without a specified cell, and raise a warning."""
    with pytest.warns(UserWarning) as record:
        descriptors = get_descriptors(CO)
    assert len(record) == 1
    assert (
        record[0].message.args[0] == 'Using default unit cell (cubic with side 100 Å).'
    )
    assert descriptors.shape == (2, 52)


def test_get_descriptors_NEP2_independent_of_species(PbTe, CO):
    """NEP2 should give the same descriptors regardless of atom species."""
    descriptors_PbTe = get_descriptors(PbTe)
    descriptors_CO = get_descriptors(CO)
    assert np.allclose(descriptors_CO, descriptors_PbTe, atol=1e-12, rtol=0)


def test_get_descriptors_NEP2_several_atoms_same_species(CC):
    """NEP2 should get the descritors for a single component system"""
    descriptors_CC = get_descriptors(CC)
    assert descriptors_CC.shape == (2, 52)
    assert descriptors_CC.dtype == np.float64
    assert not np.all(np.isclose(descriptors_CC, 0))


def test_get_descriptors_dummy_NEP2_several_atom_species(C, CO, CON):
    """Verifies the dummy NEP model has the correct number of parameters."""
    # C
    get_descriptors(C, debug=True)
    tmp_dir = './tmp_nepy/'
    C_dummy_parameters = _load_nep_from_file(f'{tmp_dir}/nep.txt').split('\n')[6:]
    _clean_tmp_dir(tmp_dir)
    assert len(C_dummy_parameters) == 1698
    # CO
    get_descriptors(CO, debug=True)
    tmp_dir = './tmp_nepy/'
    CO_dummy_parameters = _load_nep_from_file(f'{tmp_dir}/nep.txt').split('\n')[6:]
    _clean_tmp_dir(tmp_dir)
    assert len(CO_dummy_parameters) == 1773
    # CON
    get_descriptors(CON, debug=True)
    tmp_dir = './tmp_nepy/'
    CON_dummy_parameters = _load_nep_from_file(f'{tmp_dir}/nep.txt').split('\n')[6:]
    _clean_tmp_dir(tmp_dir)
    assert len(CON_dummy_parameters) == 1898


def test_get_descriptors_NEP2_dummy(PbTe):
    """Case: No NEP model supplied; using dummy NEP2 model.
    Compares results to output from `nep_cpu`
    """
    descriptors_PbTe = get_descriptors(PbTe)
    expected_PbTe = np.loadtxt(
        'tests/example_output/PbTe_NEP2_dummy_PbTe_2atom_descriptor.out'
    )
    assert np.allclose(descriptors_PbTe, expected_PbTe, atol=1e-12, rtol=0)


def test_get_descriptors_NEP3(PbTe):
    """Case: NEP3 model supplied. Compares results to output from `nep_cpu`"""
    nep3 = 'tests/nep_models/nep3_v3.3.1_PbTe_Fan22.txt'
    descriptors_PbTe = get_descriptors(PbTe, model_filename=nep3)
    expected_PbTe = np.loadtxt(
        'tests/example_output/nep3_v3.3.1_PbTe_Fan22_PbTe_2atom_descriptor.out'
    )
    assert np.allclose(descriptors_PbTe, expected_PbTe, atol=1e-12, rtol=0)


def test_get_descriptors_debug(PbTe):
    """Check that the generated files are accessible in the debug directory"""
    get_descriptors(PbTe, debug=True)
    tmp_dir = './tmp_nepy/'
    PbTe_dummy = _load_nep_from_file(f'{tmp_dir}/nep.txt')
    _clean_tmp_dir(tmp_dir)
    assert 'nep 2 Te Pb' in PbTe_dummy


def test_get_descriptors_debug_directory_exists(PbTe):
    """Should fail if debug directory already exists from an earlier calculation"""
    get_descriptors(PbTe, debug=True)
    tmp_dir = './tmp_nepy/'
    with pytest.raises(FileExistsError) as e:
        get_descriptors(PbTe, debug=True)
    assert 'Please delete or move the conflicting directory' in str(e)
    _clean_tmp_dir(tmp_dir)


# --- get_potential_forces_and_virials ---
def test_get_potential_forces_and_virials_NEP3(PbTe):
    """Case: NEP3 model supplied. Compares results to output from `nep_cpu`"""
    nep3 = 'tests/nep_models/nep3_v3.3.1_PbTe_Fan22.txt'
    energies, forces, virials = get_potential_forces_and_virials(
        PbTe, model_filename=nep3
    )

    expected_forces = get_expected(
        'tests/example_output/nep3_v3.3.1_PbTe_Fan22_PbTe_2atom_force.out'
    )
    expected_virials = get_expected(
        'tests/example_output/nep3_v3.3.1_PbTe_Fan22_PbTe_2atom_virial.out'
    )

    assert energies.shape == (2,)
    assert forces.shape == (2, 3)
    assert virials.shape == (2, 9)
    assert np.allclose(forces, expected_forces, atol=1e-12, rtol=0)
    assert np.allclose(virials, expected_virials, atol=1e-12, rtol=0)


def test_get_potential_forces_and_virials_NEP3_debug(PbTe):
    """Compares result with debug flag enabled."""
    nep3 = 'tests/nep_models/nep3_v3.3.1_PbTe_Fan22.txt'
    energies, forces, virials = get_potential_forces_and_virials(
        PbTe, model_filename=nep3, debug=True
    )

    expected_forces = get_expected(
        'tests/example_output/nep3_v3.3.1_PbTe_Fan22_PbTe_2atom_force.out'
    )
    expected_virials = get_expected(
        'tests/example_output/nep3_v3.3.1_PbTe_Fan22_PbTe_2atom_virial.out'
    )

    assert energies.shape == (2,)
    assert forces.shape == (2, 3)
    assert virials.shape == (2, 9)
    assert np.allclose(forces, expected_forces, atol=1e-12, rtol=0)
    assert np.allclose(virials, expected_virials, atol=1e-12, rtol=0)


def test_get_potential_forces_and_virials_dummy_NEP2(CO):
    """Dummy NEP2 model supplied. Compares results to output from `nep_cpu` for another system"""
    nep2_dummy = 'tests/nep_models/CO_NEP2_dummy.txt'
    energies, forces, virials = get_potential_forces_and_virials(
        CO, model_filename=nep2_dummy
    )

    expected_forces = get_expected(
        'tests/example_output/CO_NEP2_dummy_CO_2atom_force.out'
    )
    expected_virials = get_expected(
        'tests/example_output/CO_NEP2_dummy_CO_2atom_virial.out'
    )

    assert energies.shape == (2,)
    assert forces.shape == (2, 3)
    assert virials.shape == (2, 9)
    assert np.allclose(forces, expected_forces, atol=1e-12, rtol=0)
    assert np.allclose(virials, expected_virials, atol=1e-12, rtol=0)


def test_get_potential_forces_and_virials_no_cell(CO):
    """Should work with default cell if no cell is supplied"""
    nep2_dummy = 'tests/nep_models/CO_NEP2_dummy.txt'
    with pytest.warns(UserWarning) as record:
        energies, forces, virials = get_potential_forces_and_virials(
            CO, model_filename=nep2_dummy
        )

    expected_forces = get_expected(
        'tests/example_output/CO_NEP2_dummy_CO_2atom_force.out'
    )
    expected_virials = get_expected(
        'tests/example_output/CO_NEP2_dummy_CO_2atom_virial.out'
    )

    assert len(record) == 1
    assert (
        record[0].message.args[0] == 'Using default unit cell (cubic with side 100 Å).'
    )
    assert energies.shape == (2,)
    assert forces.shape == (2, 3)
    assert virials.shape == (2, 9)
    assert np.allclose(forces, expected_forces, atol=1e-12, rtol=0)
    assert np.allclose(virials, expected_virials, atol=1e-12, rtol=0)


def test_get_potential_forces_and_virials_several_of_same_species(CC):
    """Check that forces are correct for a CC system"""
    nep = 'tests/nep_models/C_NEP2_dummy.txt'
    energies, forces, virials = get_potential_forces_and_virials(
        CC, model_filename=nep
    )

    expected_forces = get_expected(
        'tests/example_output/C_NEP2_dummy_C_2atom_force.out'
    )
    expected_virials = get_expected(
        'tests/example_output/C_NEP2_dummy_C_2atom_virial.out'
    )

    assert energies.shape == (2,)
    assert forces.shape == (2, 3)
    assert virials.shape == (2, 9)
    assert np.allclose(forces, expected_forces, atol=1e-12, rtol=0)
    assert np.allclose(virials, expected_virials, atol=1e-12, rtol=0)


def test_get_potential_forces_and_virials_several_different_species(CON):
    """Check that forces are correct for a CON system.
    Note that these forces should be exactly zero for this system
    since the NEP2 dummy potential treats all atom species as identical atm.
    """
    nep = 'tests/nep_models/CON_NEP2_dummy.txt'
    energies, forces, virials = get_potential_forces_and_virials(
        CON, model_filename=nep
    )

    expected_forces = get_expected(
        'tests/example_output/CON_NEP2_dummy_CON_3atom_force.out'
    )
    expected_virials = get_expected(
        'tests/example_output/CON_NEP2_dummy_CON_3atom_virial.out'
    )

    assert energies.shape == (3,)
    assert forces.shape == (3, 3)
    assert virials.shape == (3, 9)

    assert np.allclose(forces, expected_forces, atol=1e-12, rtol=0)
    assert np.allclose(forces, np.zeros((3, 3)), atol=1e-12, rtol=0)
    assert np.allclose(virials, expected_virials, atol=1e-12, rtol=0)
    assert np.allclose(virials, np.zeros((3, 9)), atol=1e-12, rtol=0)


def test_get_potential_forces_and_virials_no_potential(PbTe):
    """Tries to get potentials, forces and virials without specifying potential"""
    with pytest.raises(ValueError) as e:
        get_potential_forces_and_virials(PbTe)
    assert 'Model must be defined!' in str(e)


def test_get_potential_forces_and_virials_invalid_potential(PbTe):
    """Tries to get potential with a dipole potential"""
    with pytest.raises(ValueError) as e:
        get_potential_forces_and_virials(
            PbTe, model_filename='tests/nep_models/nep4_dipole_Christian.txt'
        )
    assert (
        'A NEP model trained for predicting energies and forces must be used.' in str(e)
    )


def test_get_potential_forces_and_virials_malformed_potential(tmp_path, PbTe):
    """Tries to get potential energy with a malformed potential"""
    p = tmp_path / 'nep.txt'
    p.write_text((
        'npe3_lmao\n'
        'cutoff 8 4\n'
        'n_max 4 4\n'
        'l_max 4 2\n'
        'ANN 30 0\n'
        ' 1.0'
    ))
    with pytest.raises(ValueError) as e:
        get_potential_forces_and_virials(PbTe, model_filename=str(p))
    assert 'Unknown field: npe3_lmao' in str(
        e
    )


# --- get_dipole ---
def test_get_dipole_NEP3(nep3_dipole):
    """Case: NEP3 model supplied. Compares results to output from DFT."""
    structure = read('tests/example_files/dipole/test.xyz')

    dipole = get_dipole(structure, model_filename=nep3_dipole)
    dft_dipole = structure.info['dipole']
    delta = dipole - dft_dipole
    assert dipole.shape == (3,)
    assert np.allclose(
        [-0.07468218, -0.03891397, -0.11160894], delta, atol=1e-12, rtol=1e-5
    )


def test_get_dipole_no_potential(PbTe):
    """Tries to get dipole without specifying potential"""
    with pytest.raises(ValueError) as e:
        get_dipole(PbTe)
    assert 'Model must be defined!' in str(e)


def test_get_dipole_invalid_potential(PbTe):
    """Tries to get dipole with a non-dipole potential"""
    with pytest.raises(ValueError) as e:
        get_dipole(PbTe, model_filename='tests/nep_models/nep4_PbTe.txt')
    assert 'A NEP model trained for predicting dipoles must be used.' in str(e)


def test_dipole_consistent_CPU_GPU(nep3_dipole):
    """
    Make sure that the NEP_CPU implementation yields the same results as
    predicting with the NEP executable
    """
    structure = read('tests/example_files/dipole/test.xyz')
    structure = _set_dummy_energy_forces(structure)

    dipole = get_dipole(structure, model_filename=nep3_dipole)
    nep_dipole = _predict_dipole_batch(
        structures=[structure],
        model_filename=nep3_dipole,
        nep_command='nep',
    ) * len(structure)
    delta = dipole - nep_dipole
    assert nep_dipole.shape == (1, 3)
    assert np.allclose(
        [1.05823531e-04, 5.87483347e-05, -4.77966090e-06], delta, atol=1e-12, rtol=1e-5
    )


# --- get_dipole_gradient ---
def test_get_dipole_gradient(nep3_dipole):
    """Dipole gradients are computed using finite differences"""
    structure = read('tests/example_files/dipole/test.xyz')
    N = len(structure)
    # Test python implementation
    gradient_forward_python = get_dipole_gradient(
        structure,
        model_filename=nep3_dipole,
        displacement=1e-2,
        backend='python',
        method='forward difference',
        charge=1.0,
    )

    gradient_central_python = get_dipole_gradient(
        structure,
        model_filename=nep3_dipole,
        displacement=1e-2,
        backend='python',
        method='central difference',
        charge=1.0,
    )

    assert gradient_forward_python.shape == (N, 3, 3)
    assert gradient_central_python.shape == (N, 3, 3)
    assert not np.allclose(
        gradient_central_python, gradient_forward_python, atol=1e-12, rtol=1e-6
    )
    assert not np.allclose(gradient_forward_python, 0, atol=1e-12, rtol=1e-6)

    # Test nep implementation
    gradient_forward_nep = get_dipole_gradient(
        structure,
        model_filename=nep3_dipole,
        displacement=1e-2,  # Results seems to become unstable below 1e-2; rounding errors?
        backend='nep',
        method='forward difference',
        charge=1.0,
        nep_command='nep',
    )

    gradient_central_nep = get_dipole_gradient(
        structure,
        model_filename=nep3_dipole,
        displacement=1e-2,
        backend='nep',
        method='central difference',
        charge=1.0,
        nep_command='nep',
    )

    assert gradient_forward_nep.shape == (N, 3, 3)
    assert gradient_central_nep.shape == (N, 3, 3)
    assert np.allclose(
        gradient_forward_nep, gradient_forward_python, atol=1e-1, rtol=1e-6
    )
    assert np.allclose(
        gradient_central_nep, gradient_central_python, atol=1e-1, rtol=1e-6
    )

    # Test CPU implementation
    gradient_forward_cpp = get_dipole_gradient(
        structure,
        model_filename=nep3_dipole,
        displacement=1e-2,
        backend='c++',
        method='forward difference',
        charge=1.0,
    )

    gradient_central_cpp = get_dipole_gradient(
        structure,
        model_filename=nep3_dipole,
        displacement=1e-2,
        backend='c++',
        method='central difference',
        charge=1.0,
    )

    assert gradient_forward_cpp.shape == (N, 3, 3)
    assert gradient_central_cpp.shape == (N, 3, 3)
    assert np.allclose(
        gradient_forward_cpp, gradient_forward_python, atol=1e-12, rtol=1e-6
    )
    assert np.allclose(
        gradient_central_cpp, gradient_central_python, atol=1e-12, rtol=1e-6
    )


def test_get_dipole_gradient_second_order(nep3_dipole):
    """Compare second order central difference to first order"""
    structure = read('tests/example_files/dipole/test.xyz')
    N = len(structure)

    gradient_first_python = get_dipole_gradient(
        structure,
        model_filename=nep3_dipole,
        displacement=1e-2,
        backend='python',
        method='central difference',
        charge=1.0,
    )
    gradient_second_python = get_dipole_gradient(
        structure,
        model_filename=nep3_dipole,
        displacement=1e-2,
        backend='python',
        method='second order central difference',
        charge=1.0,
    )
    assert gradient_first_python.shape == (N, 3, 3)
    assert gradient_second_python.shape == (N, 3, 3)
    # Second order should give somewhat the same results as first order
    # I.e. on the same order.
    assert np.allclose(
        gradient_first_python, gradient_second_python, atol=1e-1, rtol=1e-1
    )

    gradient_first_cpp = get_dipole_gradient(
        structure,
        model_filename=nep3_dipole,
        displacement=1e-2,
        backend='c++',
        method='central difference',
        charge=1.0,
    )

    gradient_second_cpp = get_dipole_gradient(
        structure,
        model_filename=nep3_dipole,
        displacement=1e-2,
        backend='c++',
        method='second order central difference',
        charge=1.0,
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


def test_get_dipole_gradient_numeric(nep3_dipole):
    """Compare gradient to manually computed, for a two atom system"""
    structure = read('tests/example_files/dipole/test.xyz')[:2]

    # Calculate expected dipole gradient
    # Correct dipoles by the permanent dipole
    # charge = 2.0
    # copy = structure.copy()
    # dipole = (
    #     get_dipole(copy, model_filename=nep3_dipole) + charge * copy.get_center_of_mass()
    # )

    # displacement = 0.01
    # positions = copy.get_positions()
    # positions[0, 0] += displacement  # move in x direction
    # copy.set_positions(positions)
    # dipole_forward = (
    #     get_dipole(copy, model_filename=nep3_dipole) + charge * copy.get_center_of_mass()
    # )

    # expected = (dipole_forward - dipole) / displacement
    # print(expected)
    expected = [733.95084217, 4.56472784, 16.75684465]
    gradient_python = get_dipole_gradient(
        structure,
        model_filename=nep3_dipole,
        displacement=0.01,
        backend='python',
        method='forward difference',
        charge=2.0,
    )
    gradient = gradient_python[0, 0, :]
    assert np.allclose(expected, gradient, atol=1e-12, rtol=1e-6)

    gradient_nep = get_dipole_gradient(
        structure,
        model_filename=nep3_dipole,
        displacement=0.01,
        backend='nep',
        method='forward difference',
        charge=2.0,
        nep_command='nep',
    )
    gradient = gradient_nep[0, 0, :]
    assert np.allclose(expected, gradient, atol=1e-6, rtol=1e-3)

    gradient_cpp = get_dipole_gradient(
        structure,
        model_filename=nep3_dipole,
        displacement=0.01,
        backend='c++',
        method='forward difference',
        charge=2.0,
    )
    gradient = gradient_cpp[0, 0, :]
    assert np.allclose(expected, gradient, atol=1e-12, rtol=1e-6)


def test_get_dipole_gradient_numeric_without_correction(nep3_dipole):
    """Compare gradient to manually computed, for a two atom system"""
    structure = read('tests/example_files/dipole/test.xyz')[:2]

    # Calculate expected dipole gradient
    # copy = structure.copy()
    # dipole = get_dipole(copy, model_filename=nep3_dipole)
    # displacement = 0.01
    # positions = copy.get_positions()
    # positions[0, 0] += displacement  # move in x direction
    # copy.set_positions(positions)
    # dipole_forward = get_dipole(copy, model_filename=nep3_dipole)
    # expected = (dipole_forward - dipole) / displacement
    # print(expected)
    expected = [733.14383155, 4.56472784, 16.75684465]
    gradient_python = get_dipole_gradient(
        structure,
        model_filename=nep3_dipole,
        displacement=0.01,
        backend='python',
        method='forward difference',
        charge=0.0,
    )
    gradient = gradient_python[0, 0, :]
    assert np.allclose(expected, gradient, atol=1e-12, rtol=1e-6)

    gradient_nep = get_dipole_gradient(
        structure,
        model_filename=nep3_dipole,
        displacement=0.01,
        backend='nep',
        method='forward difference',
        charge=0.0,
        nep_command='nep',
    )
    gradient = gradient_nep[0, 0, :]
    assert np.allclose(expected, gradient, atol=1e-6, rtol=1e-3)

    gradient_cpp = get_dipole_gradient(
        structure,
        model_filename=nep3_dipole,
        displacement=0.01,
        backend='c++',
        method='forward difference',
        charge=0.0,
    )
    gradient = gradient_cpp[0, 0, :]
    assert np.allclose(expected, gradient, atol=1e-12, rtol=1e-6)


def test_get_dipole_gradient_nep_too_small_displacement(nep3_dipole):
    """
    NEP implementation seems susceptible to small displacements,
    probably because of rounding errors.
    """
    structure = read('tests/example_files/dipole/test.xyz')
    N = len(structure)

    with pytest.warns(UserWarning) as record:
        gradient_nep = get_dipole_gradient(
            structure,
            model_filename=nep3_dipole,
            displacement=1e-6,
            backend='nep',
            method='forward difference',
            nep_command='nep',
        )
    assert (
        record[0].message.args[0]
        == 'Dipole gradients with nep are unstable for displacements < 0.01 Å.'
    )
    assert gradient_nep.shape == (N, 3, 3)


def test_get_dipole_gradient_invalid_potential(PbTe):
    """Tries to get dipole gradient with a non-dipole potential"""
    with pytest.raises(ValueError) as e:
        get_dipole_gradient(
            PbTe,
            model_filename='tests/nep_models/nep4_PbTe.txt',
            displacement=0.01,
            method='lmao',
            backend='c#',
        )
    assert 'A NEP model trained for predicting dipoles must be used.' in str(e)


def test_get_dipole_gradient_no_potential(PbTe):
    """Tries to get dipole gradient without a potential"""
    with pytest.raises(ValueError) as e:
        get_dipole_gradient(
            PbTe,
            model_filename=None,
            displacement=0.01,
            method='lmao',
            backend='c#',
        )
    assert 'Model must be defined!' in str(e)


def test_get_dipole_gradient_invalid_backend(PbTe):
    """Tries to get dipole gradient whilst specifying an invalid backend"""
    with pytest.raises(ValueError) as e:
        get_dipole_gradient(
            PbTe,
            model_filename='tests/nep_models/nep4_dipole_Christian.txt',
            displacement=0.01,
            method='lmao',
            backend='c#',
        )
    assert 'Invalid backend c#' in str(e)


@pytest.mark.parametrize('backend', ['nep', 'python', 'c++'])
def test_get_dipole_gradient_invalid_method(PbTe, backend):
    """Tries to get dipole gradient whilst specifying an invalid method"""
    print(backend)
    with pytest.raises(ValueError) as e:
        get_dipole_gradient(
            PbTe,
            model_filename='tests/nep_models/nep4_dipole_Christian.txt',
            displacement=0.01,
            method='lmao',
            backend=backend,
        )
    assert 'Invalid method lmao for calculating gradient' in str(e)


@pytest.mark.parametrize('backend', ['nep', 'python', 'c++'])
def test_get_dipole_gradient_invalid_displacement(backend, PbTe):
    """Tries to get dipole gradient with an invalid displacement"""
    with pytest.raises(ValueError) as e:
        get_dipole_gradient(
            PbTe,
            model_filename='tests/nep_models/nep4_dipole_Christian.txt',
            displacement=0,
            backend=backend,
        )
    assert 'Displacement must be > 0 Å' in str(e)


def latent_space_reference(structure: Atoms, model_filename: str) -> np.ndarray:
    """Reference function for computing the latent space representation of a structure"""
    potential = read_model(model_filename)
    # Network parameters
    w0 = potential.ann_parameters['all_species']['w0']
    b0 = potential.ann_parameters['all_species']['b0']
    w1 = potential.ann_parameters['all_species']['w1']
    d = get_descriptors(structure, model_filename=model_filename)
    z0 = w0 @ d.T
    a0 = np.tanh(z0 - b0)
    z1 = a0.T * w1

    return z1


# --- get_polarizability ---
def test_get_polarizability_NEP3(nep3_pol):
    """Case: NEP3 model supplied. Compares results to output from DFT."""
    structure = read('tests/example_files/polarizability/test.xyz')

    pol = get_polarizability(structure, model_filename=nep3_pol)
    dft_pol = structure.info['pol'].reshape(3, 3)
    delta = pol - dft_pol

    assert pol.shape == (3, 3)
    assert np.allclose(delta.mean(), 0.0323862, atol=1e-12, rtol=1e-5)


def test_get_polarizability_no_potential(PbTe):
    """Tries to get dipole without specifying potential"""
    with pytest.raises(ValueError) as e:
        get_polarizability(PbTe)
    assert 'Model must be defined!' in str(e)


def test_get_polarizability_invalid_potential(PbTe):
    """Tries to get polarizability with a non-dipole potential"""
    with pytest.raises(ValueError) as e:
        get_polarizability(PbTe, model_filename='tests/nep_models/nep4_PbTe.txt')
    assert 'A NEP model trained for predicting polarizability must be used.' in str(e)


# --- get_latent_space ---
def test_get_latent_space_NEP3(PbTe):
    """Case: NEP3 model supplied. Returns a latent space with expected shape."""
    nep3 = 'tests/nep_models/nep3_v3.3.1_PbTe_Fan22.txt'
    latent = get_latent_space(PbTe, model_filename=nep3)
    reference_latent = latent_space_reference(PbTe, nep3)
    assert latent.shape == (2, 30)
    assert np.allclose(latent, reference_latent)


def test_get_latent_space_no_potential(PbTe):
    """Tries to get latent space without specifying potential"""
    with pytest.raises(ValueError) as e:
        get_latent_space(PbTe)
    assert 'Model must be defined!' in str(e)
