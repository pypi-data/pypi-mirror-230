from typing import List

import numpy as np
from ase import Atoms
from ase.io import read, write
from pandas import DataFrame


def read_kappa(filename: str) -> DataFrame:
    """Parses a file in ``kappa.out`` format from GPUMD and returns the
    content as a data frame. More information concerning file format,
    content and units can be found `here
    <https://gpumd.org/gpumd/output_files/kappa_out.html>`__.

    Parameters
    ----------
    filename
        input file name

    """
    data = np.loadtxt(filename)
    if isinstance(data[0], np.float64):
        # If only a single row in kappa.out, append a dimension
        data = data.reshape(1, -1)
    tags = 'kx_in kx_out ky_in ky_out kz_tot'.split()
    if len(data[0]) != len(tags):
        raise ValueError(f'Input file contains {len(data[0])} data columns.'
                         f' Expected {len(tags)} columns.')
    df = DataFrame(data=data, columns=tags)
    df['kx_tot'] = df.kx_in + df.kx_out
    df['ky_tot'] = df.ky_in + df.ky_out
    return df


def read_hac(filename: str) -> DataFrame:
    """Parses a file in ``hac.out`` format from GPUMD and returns the
    content as a data frame. More information concerning file format,
    content and units can be found `here
    <https://gpumd.org/gpumd/output_files/hac_out.html>`__.

    Parameters
    ----------
    filename
        input file name

    """
    data = np.loadtxt(filename)
    if isinstance(data[0], np.float64):
        # If only a single row in hac.out, append a dimension
        data = data.reshape(1, -1)
    tags = 'time'
    tags += ' jin_jtot_x jout_jtot_x jin_jtot_y jout_jtot_y jtot_jtot_z'
    tags += ' kx_in kx_out ky_in ky_out kz_tot'
    tags = tags.split()
    if len(data[0]) != len(tags):
        raise ValueError(f'Input file contains {len(data[0])} data columns.'
                         f' Expected {len(tags)} columns.')
    df = DataFrame(data=data, columns=tags)
    df['kx_tot'] = df.kx_in + df.kx_out
    df['ky_tot'] = df.ky_in + df.ky_out
    # remove columns with less relevant data to save space
    for col in df:
        if 'jtot' in col or '_in' in col:
            del df[col]
    return df


def read_thermo(filename: str,
                natoms: int = 1) -> DataFrame:
    """Parses a file in ``thermo.out`` format from GPUMD and returns the
    content as a data frame. More information concerning file format,
    content and units can be found `here
    <https://gpumd.org/gpumd/output_files/thermo_out.html>`__.

    Parameters
    ----------
    filename
        input file name
    natoms
        number of atoms; used to normalize energies

    """
    data = np.loadtxt(filename)
    if isinstance(data[0], np.float64):
        # If only a single row in loss.out, append a dimension
        data = data.reshape(1, -1)
    if len(data[0]) == 9:
        # orthorhombic box
        tags = 'temperature kinetic_energy potential_energy'
        tags += ' stress_xx stress_yy stress_zz'
        tags += ' cell_xx cell_yy cell_zz'
    elif len(data[0]) == 12:
        # orthorhombic box with stresses in Voigt notation (v3.3.1+)
        tags = 'temperature kinetic_energy potential_energy'
        tags += ' stress_xx stress_yy stress_zz stress_yz stress_xz stress_xy'
        tags += ' cell_xx cell_yy cell_zz'
    elif len(data[0]) == 15:
        # triclinic box
        tags = 'temperature kinetic_energy potential_energy'
        tags += ' stress_xx stress_yy stress_zz'
        tags += ' cell_xx cell_xy cell_xz cell_yx cell_yy cell_yz cell_zx cell_zy cell_zz'
    elif len(data[0]) == 18:
        # triclinic box with stresses in Voigt notation (v3.3.1+)
        tags = 'temperature kinetic_energy potential_energy'
        tags += ' stress_xx stress_yy stress_zz stress_yz stress_xz stress_xy'
        tags += ' cell_xx cell_xy cell_xz cell_yx cell_yy cell_yz cell_zx cell_zy cell_zz'
    else:
        raise ValueError(f'Input file contains {len(data[0])} data columns.'
                         ' Expected 9, 12, 15 or 18 columns.')
    df = DataFrame(data=data, columns=tags.split())
    assert natoms > 0, 'natoms must be positive'
    df.kinetic_energy /= natoms
    df.potential_energy /= natoms
    return df


def read_xyz(filename: str) -> Atoms:
    """
    Read the structure input file (`model.xyz`) for GPUMD and return the
    structure along with run input parameters from the file.

    This is a wrapper function around :func:`ase.io.read_xyz` since the ASE implementation does
    not read velocities properly.

    Parameters
    ----------
    filename
        Name of file from which to read the structure

    Returns
    -------
    structure as ASE Atoms object with additional per-atom arrays
    representing atomic masses, velocities etc.
    """
    structure = read(filename, format='extxyz')
    if structure.has('vel'):
        structure.set_velocities(structure.get_array('vel'))
    return structure


def write_xyz(filename: str,
              structure: Atoms,
              groupings: List[List[List[int]]] = None):
    """
    Writes a structure into GPUMD input format (`model.xyz`).

    Parameters
    ----------
    filename
        Name of file to which the structure should be written
    structure
        Input structure
    groupings
        Groups into which the individual atoms should be divided in the form of
        a list of list of lists. Specifically, the outer list corresponds to
        the grouping methods, of which there can be three at the most, which
        contains a list of groups in the form of lists of site indices. The
        sum of the lengths of the latter must be the same as the total number
        of atoms.

    Raises
    ------
    ValueError
        Raised if parameters are incompatible
    """
    # Make a local copy of the atoms object
    _structure = structure.copy()

    # Check velocties parameter
    velocities = _structure.get_velocities()
    if velocities is None or np.max(np.abs(velocities)) < 1e-6:
        has_velocity = 0
    else:
        has_velocity = 1

    # Check groupings parameter
    if groupings is None:
        number_of_grouping_methods = 0
    else:
        number_of_grouping_methods = len(groupings)
        if number_of_grouping_methods > 3:
            raise ValueError('There can be no more than 3 grouping methods!')
        for g, grouping in enumerate(groupings):
            all_indices = [i for group in grouping for i in group]
            if len(all_indices) != len(_structure) or \
                    set(all_indices) != set(range(len(_structure))):
                raise ValueError(f'The indices listed in grouping method {g} are'
                                 ' not compatible with the input'
                                 ' structure!')

    # Allowed keyword=value pairs. Use ASEs extyz write functionality.:
    #   pbc="pbc_a pbc_b pbc_c"
    #   lattice="ax ay az bx by bz cx cy cz"
    #   properties=property_name:data_type:number_of_columns
    #       species:S:1
    #       pos:R:3
    #       mass:R:1
    #       vel:R:3
    #       group:I:number_of_grouping_methods
    _structure.new_array('mass', _structure.get_masses())
    if has_velocity:
        _structure.new_array('vel', _structure.get_velocities())
    if groupings is not None:
        group_indices = np.array([
            [
                [group_index for group_index, group in enumerate(
                    grouping) if structure_idx in group] for grouping in groupings
            ]
            for structure_idx in range(len(_structure))]).squeeze()  # pythoniccc
        _structure.new_array('group', group_indices)

    write(filename=filename, images=_structure, write_info=True, format='extxyz')
