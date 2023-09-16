import contextlib
import os
import shutil
import tempfile
import warnings
from typing import List, Optional, Tuple, Union

import numpy as np
from ase import Atoms

import _nepy
from calorine.nep.model import _get_nep_contents


def _create_dummy_nep2(model_filename: str, symbols: List[str]) -> None:
    """Create a dummy NEP2 model, i.e., a model for which there are no descriptor parameters.
    This is to be used when one wants descriptors not pertaining to a specific NEP3 model.

    Parameters
    ----------
    model_filename
        Path to which the NEP2 model will be saved.
    symbols
        Atomic elements in the configuration for which to compute descriptors.
    """
    unique_symbols = []
    for sym in symbols:
        if sym not in unique_symbols:
            unique_symbols.append(sym)
    with open(model_filename, 'w') as f:
        f.write(f'nep {len(unique_symbols)} ')
        for symbol in unique_symbols:
            f.write(f'{symbol} ')
        f.write('\n')
        # Write rest of header
        f.write('cutoff 6 4\nn_max 15 8\nl_max 4\nANN 30 0\n')
        # Write dummy parameters
        # The number of parameters in the network is:
        # N_par = (N_des+2)N_neu + 1 + N_typ**2 (n_max^R + n_max^A + 2)
        # Default settings: 1621 + N_typ**2 * 25
        # The last 52 1:s are the normalization parameters for the descriptors.
        for _ in range(1621 + len(unique_symbols) ** 2 * 25 + 52):
            f.write(f'  {1e0:e}\n')


def _create_tmp_dir(debug: bool) -> str:
    """Create temporary directory.

    Parameters
    ----------
    debug
        Flag that indicates if debugging. Use a hardcoded path when debugging.

    Returns
    -------
    str
         Path to temporary directory
    """
    if debug:
        tmp_dir = './tmp_nepy/'
        # os.mkdir(tmp_dir)
        try:
            os.mkdir(tmp_dir)
            return tmp_dir
        except FileExistsError:
            raise FileExistsError('Please delete or move the conflicting directory.')
    return tempfile.mkdtemp()


def _clean_tmp_dir(directory: str) -> None:
    """Remove temporary directory.

    Parameters
    ----------
    directory
        Path to temporary directory
    """
    shutil.rmtree(directory)


def _get_atomic_properties(
    structure: Atoms,
) -> Tuple[List[float], List[str], List[float]]:
    """Fetches cell, symbols and positions for a structure. Since NEP_CPU requires a cell, if the
    structure has no cell a default cubic cell with a side of 100 Å will be used.

    Parameters
    ----------
    structure
        Atoms object representing the structure.

    Returns
    -------
    List[float]
        Cell vectors
    List[str]
        Atomic species
    List[float]
        Atom positions
    List[float]
        Atom masses
    """
    if structure.cell.rank == 0:
        warnings.warn('Using default unit cell (cubic with side 100 Å).')
        set_default_cell(structure)

    c = structure.get_cell(complete=True).flatten()
    cell = [c[0], c[3], c[6], c[1], c[4], c[7], c[2], c[5], c[8]]

    symbols = structure.get_chemical_symbols()
    positions = list(
        structure.get_positions().T.flatten()
    )  # [x1, ..., xN, y1, ... yN,...]
    masses = structure.get_masses()
    return cell, symbols, positions, masses


def _setup_nepy(
    model_filename: str,
    natoms: int,
    cell: List[float],
    symbols: List[str],
    positions: List[float],
    masses: List[float],
    debug: bool,
) -> _nepy.NEPY:
    """Sets up an instance of the NEPY pybind11 interface to NEP_CPU.

    Parameters
    ----------
    model_filename
        Path to model.
    natoms:
        Number of atoms in the structure.
    cell:
        Cell vectors.
    symbols:
        Atom species.
    positions:
        Atom positions.
    masses:
        Atom masses.
    debug:
        Flag to control if the output from NEP_CPU will be printed.

    Returns
    -------
    NEPY
        NEPY interface
    """
    # Disable output from C++ code by default
    if debug:
        nepy = _nepy.NEPY(model_filename, natoms, cell, symbols, positions, masses)
    else:
        with open(os.devnull, 'w') as f:
            with contextlib.redirect_stdout(f):
                with contextlib.redirect_stderr(f):
                    nepy = _nepy.NEPY(
                        model_filename, natoms, cell, symbols, positions, masses
                    )
    return nepy


def set_default_cell(structure: Atoms, box_length: float = 100):
    """Adds a cubic box to an Atoms object. Atoms object is edited in-place.

    Parameters
    ----------
    structure
        Structure to add box to
    box_length
        Cubic box side length in Å, by default 100
    """
    structure.set_cell([[box_length, 0, 0], [0, box_length, 0], [0, 0, box_length]])
    structure.center()


def get_descriptors(
    structure: Atoms, model_filename: Optional[str] = None, debug: bool = False
) -> np.ndarray:
    """Calculates the NEP descriptors for a given structure. A NEP model defined by a nep.txt
    can additionally be provided to get the NEP3 model specific descriptors. If no model is
    provided, a dummy NEP2 model suitable for the provided structure will be created and used.

    Parameters
    ----------
    structure
        Input structure
    model_filename
        Path to NEP model in ``nep.txt`` format. Defaults to ``None``.
    debug
        Flag to toggle debug mode. Makes the generated dummy NEP2 model available
        in a local tmp directory, as well as prints GPUMD output. Defaults to ``False``.

    Returns
    -------
    Descriptors for the supplied structure, with shape (natoms, descriptor components)
    """
    local_structure = structure.copy()
    natoms = len(local_structure)
    cell, symbols, positions, masses = _get_atomic_properties(local_structure)

    use_dummy_nep2_potential = model_filename is None
    if use_dummy_nep2_potential:
        tmp_dir = _create_tmp_dir(debug)
        model_filename = f'{tmp_dir}/nep.txt'
        _create_dummy_nep2(model_filename, symbols)
    else:
        tmp_dir = None

    nepy = _setup_nepy(
        model_filename, natoms, cell, symbols, positions, masses, debug
    )
    all_descriptors = nepy.get_descriptors()
    descriptors_per_atom = np.array(all_descriptors).reshape(-1, natoms).T

    if use_dummy_nep2_potential and tmp_dir and not debug:
        _clean_tmp_dir(tmp_dir)
    if use_dummy_nep2_potential and tmp_dir and debug:
        print(f'DEBUG - Directory containing dummy nep.in: {tmp_dir}')
    return descriptors_per_atom


def get_latent_space(
    structure: Atoms, model_filename: Union[str, None] = None, debug: bool = False
) -> np.ndarray:
    """Calculates the latent space representation of a structure, i.e, the activiations in
    the hidden layer. A NEP model defined by a `nep.txt` file needs to be provided.

    Parameters
    ----------
    structure
        Input structure
    model_filename
        Path to NEP model. Defaults to None.
    debug
        Flag to toggle debug mode. Prints GPUMD output. Defaults to False.

    Returns
    -------
    Activation with shape `(natoms, N_neurons)`
    """
    if model_filename is None:
        raise ValueError('Model must be defined!')
    local_structure = structure.copy()
    natoms = len(local_structure)
    cell, symbols, positions, masses = _get_atomic_properties(local_structure)

    nepy = _setup_nepy(
        model_filename, natoms, cell, symbols, positions, masses, debug
    )

    latent = nepy.get_latent_space()
    latent = np.array(latent).reshape(-1, natoms).T
    return latent


def get_potential_forces_and_virials(
    structure: Atoms, model_filename: Optional[str] = None, debug: bool = False
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Calculates the per-atom potential, forces and virials for a given structure.
    A NEP model defined by a `nep.txt` file needs to be provided.

    Parameters
    ----------
    structure
        Input structure
    model_filename
        Path to NEP model. Defaults to None.
    debug
        Flag to toggle debug mode. Prints GPUMD output. Defaults to False.

    Returns
    -------
    potential with shape `(natoms,)`
    forces with shape `(natoms, 3)`
    virials with shape `(natoms, 9)`
    """
    if model_filename is None:
        raise ValueError('Model must be defined!')

    model_type = _get_nep_contents(model_filename)[0]['model_type']
    if model_type != 'potential':
        raise ValueError(
            'A NEP model trained for predicting energies and forces must be used.'
        )

    local_structure = structure.copy()
    natoms = len(local_structure)
    cell, symbols, positions, masses = _get_atomic_properties(local_structure)

    nepy = _setup_nepy(
        model_filename, natoms, cell, symbols, positions, masses, debug
    )

    energies, forces, virials = nepy.get_potential_forces_and_virials()
    forces_per_atom = np.array(forces).reshape(-1, natoms).T
    virials_per_atom = np.array(virials).reshape(-1, natoms).T
    return np.array(energies), forces_per_atom, virials_per_atom


def get_polarizability(
    structure: Atoms,
    model_filename: Optional[str] = None,
    debug: bool = False,
) -> np.ndarray:
    """Calculates the polarizability tensor for a given structure. A NEP model defined
    by a ``nep.txt`` file needs to be provided. The model must be trained to predict the
    polarizability.

    Parameters
    ----------
    structure
        Input structure
    model_filename
        Path to NEP model in ``nep.txt`` format. Defaults to ``None``.
    debug
        Flag to toggle debug mode. Prints GPUMD output. Defaults to ``False``.

    Returns
    -------
    polarizability with shape ``(3, 3)``
    """
    if model_filename is None:
        raise ValueError('Model must be defined!')

    model_type = _get_nep_contents(model_filename)[0]['model_type']
    if model_type != 'polarizability':
        raise ValueError(
            'A NEP model trained for predicting polarizability must be used.'
        )

    local_structure = structure.copy()
    natoms = len(local_structure)
    cell, symbols, positions, masses = _get_atomic_properties(local_structure)

    nepy = _setup_nepy(
        model_filename, natoms, cell, symbols, positions, masses, debug
    )
    # Components are in order xx yy zz xy yz zx.
    pol = nepy.get_polarizability()
    polarizability = np.array([
        [pol[0], pol[3], pol[5]],
        [pol[3], pol[1], pol[4]],
        [pol[5], pol[4], pol[2]]
    ])

    return polarizability


def get_dipole(
    structure: Atoms,
    model_filename: Optional[str] = None,
    debug: bool = False,
) -> np.ndarray:
    """Calculates the dipole for a given structure. A NEP model defined by a
    ``nep.txt`` file needs to be provided.

    Parameters
    ----------
    structure
        Input structure
    model_filename
        Path to NEP model in ``nep.txt`` format. Defaults to ``None``.
    debug
        Flag to toggle debug mode. Prints GPUMD output. Defaults to ``False``.

    Returns
    -------
    dipole with shape ``(3,)``
    """
    if model_filename is None:
        raise ValueError('Model must be defined!')

    model_type = _get_nep_contents(model_filename)[0]['model_type']
    if model_type != 'dipole':
        raise ValueError('A NEP model trained for predicting dipoles must be used.')

    local_structure = structure.copy()
    natoms = len(local_structure)
    cell, symbols, positions, masses = _get_atomic_properties(local_structure)

    nepy = _setup_nepy(
        model_filename, natoms, cell, symbols, positions, masses, debug
    )
    dipole = np.array(nepy.get_dipole())

    return dipole


def get_dipole_gradient(
    structure: Atoms,
    model_filename: Optional[str] = None,
    backend: str = 'c++',
    method: str = 'central difference',
    displacement: float = 0.01,
    charge: float = 1.0,
    nep_command: str = 'nep',
    debug: bool = False,
) -> np.ndarray:
    """Calculates the dipole gradient for a given structure using finite differences.
    A NEP model defined by a `nep.txt` file needs to be provided.

    Parameters
    ----------
    structure
        Input structure
    model_filename
        Path to NEP model in ``nep.txt`` format. Defaults to ``None``.
    backend
        Backend to use for computing dipole gradient with finite differences.
        One of ``'c++'`` (CPU), ``'python'`` (CPU) and ``'nep'`` (GPU).
        Defaults to ``'c++'``.
    method
        Method for computing gradient with finite differences.
        One of 'forward difference' and 'central difference'.
        Defaults to 'central difference'
    displacement
        Displacement in Å to use for finite differences. Defaults to ``0.01``.
    charge
        System charge in units of the elemental charge.
        Used for correcting the dipoles before computing the gradient.
        Defaults to ``1.0``.
    nep_command
        Command for running the NEP executable. Defaults to ``'nep'``.
    debug
        Flag to toggle debug mode. Prints GPUMD output (if applicable). Defaults to ``False``.


    Returns
    -------
        dipole gradient with shape ``(N, 3, 3)``
    """
    if model_filename is None:
        raise ValueError('Model must be defined!')

    model_type = _get_nep_contents(model_filename)[0]['model_type']
    if model_type != 'dipole':
        raise ValueError('A NEP model trained for predicting dipoles must be used.')

    local_structure = structure.copy()

    if backend == 'c++':
        dipole_gradient = _dipole_gradient_cpp(
            local_structure,
            model_filename,
            displacement=displacement,
            method=method,
            charge=charge,
            debug=debug,
        )
    elif backend == 'python':
        dipole_gradient = _dipole_gradient_python(
            local_structure,
            model_filename,
            displacement=displacement,
            charge=charge,
            method=method,
        )
    elif backend == 'nep':
        dipole_gradient = _dipole_gradient_nep(
            local_structure,
            model_filename,
            displacement=displacement,
            method=method,
            charge=charge,
            nep_command=nep_command,
        )
    else:
        raise ValueError(f'Invalid backend {backend}')
    return dipole_gradient


def _dipole_gradient_cpp(
    structure: Atoms,
    model_filename: str,
    method: str = 'central difference',
    displacement: float = 0.01,
    charge: float = 1.0,
    debug: bool = False,
) -> np.ndarray:
    """Calculates the dipole gradient with finite differences, using NEP_CPU.

    Parameters
    ----------
    structure
        Input structure
    model_filename
        Path to NEP model in ``nep.txt`` format.
    method
        Method for computing gradient with finite differences.
        One of ``'forward difference'`` and ``'central difference'``.
        Defaults to ``'central difference'``
    displacement
        Displacement in Å to use for finite differences. Defaults to ``0.01``.
    charge
        System charge in units of the elemental charge.
        Used for correcting the dipoles before computing the gradient.
        Defaults to ``1.0``.

    Returns
    -------
        dipole gradient with shape ``(N, 3, 3)``
    """
    if displacement <= 0:
        raise ValueError('Displacement must be > 0 Å')

    implemented_methods = {
        'forward difference': 0,
        'central difference': 1,
        'second order central difference': 2,
    }

    if method not in implemented_methods.keys():
        raise ValueError(f'Invalid method {method} for calculating gradient')

    local_structure = structure.copy()
    natoms = len(local_structure)
    cell, symbols, positions, masses = _get_atomic_properties(local_structure)
    nepy = _setup_nepy(
        model_filename, natoms, cell, symbols, positions, masses, debug
    )
    dipole_gradient = np.array(
        nepy.get_dipole_gradient(displacement, implemented_methods[method], charge)
    ).reshape(natoms, 3, 3)
    return dipole_gradient


def _dipole_gradient_python(
    structure: Atoms,
    model_filename: str,
    method: str = 'central difference',
    displacement: float = 0.01,
    charge: float = 1.0,
) -> np.ndarray:
    """Calculates the dipole gradient with finite differences, using the Python and get_dipole().

    Parameters
    ----------
    structure
        Input structure
    model_filename
        Path to NEP model in ``nep.txt`` format.
    method
        Method for computing gradient with finite differences.
        One of ``'forward difference'`` and ``'central difference'``.
        Defaults to ``'central difference'``
    displacement
        Displacement in Å to use for finite differences. Defaults to ``0.01``.
    charge
        System charge in units of the elemental charge.
        Used for correcting the dipoles before computing the gradient.
        Defaults to ``1.0``.

    Returns
    -------
        dipole gradient with shape ``(N, 3, 3)``
    """
    if displacement <= 0:
        raise ValueError('Displacement must be > 0 Å')

    N = len(structure)
    if method == 'forward difference':
        # Correct all dipole by the permanent dipole, charge * center of mass
        d = (
            get_dipole(structure, model_filename)
            + charge * structure.get_center_of_mass()
        )
        d_forward = np.zeros((N, 3, 3))
        for atom in range(N):
            for cartesian in range(3):
                copy = structure.copy()
                positions = copy.get_positions()
                positions[atom, cartesian] += displacement
                copy.set_positions(positions)
                d_forward[atom, cartesian, :] = (
                    get_dipole(copy, model_filename)
                    + charge * copy.get_center_of_mass()
                )
        gradient = (d_forward - d[None, None, :]) / displacement

    elif method == 'central difference':
        d_forward = np.zeros((N, 3, 3))
        d_backward = np.zeros((N, 3, 3))
        for atom in range(N):
            for cartesian in range(3):
                # Forward displacements
                copy_forward = structure.copy()
                positions_forward = copy_forward.get_positions()
                positions_forward[atom, cartesian] += displacement
                copy_forward.set_positions(positions_forward)
                d_forward[atom, cartesian, :] = (
                    get_dipole(copy_forward, model_filename)
                    + charge * copy_forward.get_center_of_mass()
                )
                # Backwards displacement
                copy_backward = structure.copy()
                positions_backward = copy_backward.get_positions()
                positions_backward[atom, cartesian] -= displacement
                copy_backward.set_positions(positions_backward)
                d_backward[atom, cartesian, :] = (
                    get_dipole(copy_backward, model_filename)
                    + charge * copy_backward.get_center_of_mass()
                )
        gradient = (d_forward - d_backward) / (2 * displacement)
    elif method == 'second order central difference':
        # Coefficients from
        # https://en.wikipedia.org/wiki/Finite_difference_coefficient#Central_finite_difference
        d_forward_one_h = np.zeros((N, 3, 3))
        d_forward_two_h = np.zeros((N, 3, 3))
        d_backward_one_h = np.zeros((N, 3, 3))
        d_backward_two_h = np.zeros((N, 3, 3))
        for atom in range(N):
            for cartesian in range(3):
                copy = structure.copy()
                positions = copy.get_positions()
                # Forward displacements
                positions[atom, cartesian] += displacement  # + h
                copy.set_positions(positions)
                d_forward_one_h[atom, cartesian, :] = (
                    get_dipole(copy, model_filename)
                    + charge * copy.get_center_of_mass()
                )
                positions[atom, cartesian] += displacement  # + 2h total
                copy.set_positions(positions)
                d_forward_two_h[atom, cartesian, :] = (
                    get_dipole(copy, model_filename)
                    + charge * copy.get_center_of_mass()
                )
                # Backwards displacement
                positions[atom, cartesian] -= 3 * displacement  # 2h - 3h = -h
                copy.set_positions(positions)
                d_backward_one_h[atom, cartesian, :] = (
                    get_dipole(copy, model_filename)
                    + charge * copy.get_center_of_mass()
                )
                positions[atom, cartesian] -= displacement  # - 2h total
                copy.set_positions(positions)
                d_backward_two_h[atom, cartesian, :] = (
                    get_dipole(copy, model_filename)
                    + charge * copy.get_center_of_mass()
                )
            c0 = -1.0 / 12.0
            c1 = 2.0 / 3.0
            gradient = (
                c0 * d_forward_two_h
                + c1 * d_forward_one_h
                - c1 * d_backward_one_h
                - c0 * d_backward_two_h
            ) / displacement
    else:
        raise ValueError(f'Invalid method {method} for calculating gradient')
    return gradient


def _dipole_gradient_nep(
    structure: Atoms,
    model_filename: str,
    method: str = 'central difference',
    displacement: float = 0.01,
    charge: float = 1.0,
    nep_command: str = 'nep',
) -> np.ndarray:
    """Calculates the dipole gradient with finite differences, using the NEP executable.

    Parameters
    ----------
    structure
        Input structure
    model_filename
        Path to NEP model in ``nep.txt`` format.
    method
        Method for computing gradient with finite differences.
        One of ``'forward difference'`` and ``'central difference'``.
        Defaults to ``'central difference'``
    displacement
        Displacement in Å to use for finite differences. Defaults to 0.01 Å.
        Note that results are possibly unreliable for displacemen < 0.01,
        which might be due to rounding errors.
    charge
        System charge in units of the elemental charge.
        Used for correcting the dipoles before computing the gradient.
        Defaults to 1.0.
    nep_command
        Command for running the NEP executable. Defaults to ``'nep'``.


    Returns
    -------
        dipole gradient with shape ``(N, 3, 3)``
    """
    if displacement <= 0:
        raise ValueError('Displacement must be > 0 Å')

    if displacement < 1e-2:
        warnings.warn(
            'Dipole gradients with nep are unstable for displacements < 0.01 Å.'
        )

    N = len(structure)
    if method == 'forward difference':
        structure = _set_dummy_energy_forces(structure)
        structures = [structure]  # will hold 3N+1 structures
        # Correct for the constant dipole, by adding charge * center of mass
        corrections = np.zeros((3 * N + 1, 3))
        corrections[0] = charge * structure.get_center_of_mass()
        for atom in range(N):
            for cartesian in range(3):
                copy = structure.copy()
                positions = copy.get_positions()
                positions[atom, cartesian] += displacement
                copy.set_positions(positions)
                copy = _set_dummy_energy_forces(copy)
                structures.append(copy)
                corrections[1 + atom * 3 + cartesian] = (
                    charge * copy.get_center_of_mass()
                )

        dipoles = (
            _predict_dipole_batch(structures, model_filename, nep_command) * N
        )  # dipole/atom, shape (3N+1, 3)
        dipoles += corrections

        d = dipoles[0, :]
        d_forward = dipoles[1:].reshape(N, 3, 3)
        gradient = (d_forward - d[None, None, :]) / displacement

    elif method == 'central difference':
        structures_forward = []  # will hold 3N structures
        structures_backward = []  # will hold 3N structures

        # Correct for the constant dipole, by adding charge * center of mass
        corrections_forward = np.zeros((3 * N, 3))
        corrections_backward = np.zeros((3 * N, 3))

        for atom in range(N):
            for cartesian in range(3):
                # Forward displacements
                copy_forward = structure.copy()
                positions_forward = copy_forward.get_positions()
                positions_forward[atom, cartesian] += displacement
                copy_forward.set_positions(positions_forward)
                copy_forward = _set_dummy_energy_forces(copy_forward)
                structures_forward.append(copy_forward)
                corrections_forward[atom * 3 + cartesian] = (
                    charge * copy_forward.get_center_of_mass()
                )

                # Backwards displacement
                copy_backward = structure.copy()
                positions_backward = copy_backward.get_positions()
                positions_backward[atom, cartesian] -= displacement
                copy_backward.set_positions(positions_backward)
                copy_backward = _set_dummy_energy_forces(copy_backward)
                structures_backward.append(copy_backward)
                corrections_backward[atom * 3 + cartesian] = (
                    charge * copy_backward.get_center_of_mass()
                )

        structures = structures_forward + structures_backward
        dipoles = (
            _predict_dipole_batch(structures, model_filename, nep_command) * N
        )  # dipole/atom, shape (6N, 3)
        d_forward = dipoles[: 3 * N, :]
        d_backward = dipoles[3 * N :, :]

        d_forward += corrections_forward
        d_backward += corrections_backward

        d_forward = d_forward.reshape(N, 3, 3)
        d_backward = d_backward.reshape(N, 3, 3)

        gradient = (d_forward - d_backward) / (2 * displacement)
    else:
        raise ValueError(f'Invalid method {method} for calculating gradient')
    return gradient


def _set_dummy_energy_forces(structure: Atoms) -> Atoms:
    """Sets the energies and forces of structure to zero.

    Parameters
    ----------
    structure
        Input structure


    Returns
    ------- Copy of structure, with SinglePointCalculator with zero energy and force.
    """
    from ase.calculators.singlepoint import SinglePointCalculator

    copy = structure.copy()
    N = len(copy)
    energy = 0

    forces = np.zeros((N, 3))
    dummy = SinglePointCalculator(copy, **{'energy': energy, 'forces': forces})
    copy.calc = dummy
    return copy


def _predict_dipole_batch(
    structures: List[Atoms], model_filename: str, nep_command: str = 'nep'
) -> np.ndarray:
    """Predicts dipoles for a set of structures using the NEP executable
    Note that the units are in (dipole units)/atom.

    Parameters
    ----------
    structure
        Input structures
    model_filename
        Path to NEP model in ``nep.txt`` format.
    nep_command
        Command for running the NEP executable. Defaults to ``'nep'``.


    Returns
    ------- Predicted dipoles, with shape (len(structures), 3).
    """
    import shutil
    from os.path import join as join_path
    from subprocess import run
    from tempfile import TemporaryDirectory

    from calorine.nep import read_model, write_nepfile, write_structures

    with TemporaryDirectory() as directory:
        shutil.copy2(model_filename, join_path(directory, 'nep.txt'))
        model = read_model(model_filename)

        parameters = dict(
            prediction=1,
            mode=1,
            version=model.version,
            n_max=[model.n_max_radial, model.n_max_angular],
            cutoff=[model.radial_cutoff, model.angular_cutoff],
            basis_size=[model.n_basis_radial, model.n_basis_radial],
            l_max=[model.l_max_3b, model.l_max_4b, model.l_max_5b],
            neuron=model.n_neuron,
            type=[len(model.types), *model.types],
        )

        write_nepfile(parameters, directory)
        file = join_path(directory, 'train.xyz')
        write_structures(file, structures)

        # Execute nep
        completed = run([nep_command], cwd=directory, capture_output=True)
        completed.check_returncode()

        # Read results
        dipoles = np.loadtxt(join_path(directory, 'dipole_train.out'))
        if len(dipoles.shape) == 1:
            dipoles = dipoles.reshape(1, -1)
        return dipoles[:, :3]
