from os import makedirs
from os.path import exists, join as join_path
from typing import List, NamedTuple, Optional

import numpy as np
from ase import Atoms
from sklearn.model_selection import KFold

from .io import write_nepfile, write_structures


def setup_training(parameters: NamedTuple,
                   structures: List[Atoms],
                   enforced_structures: List[int] = [],
                   rootdir: str = '.',
                   n_splits: int = None,
                   seed: int = 42,
                   overwrite: bool = False,
                   ) -> None:
    """Sets up the input files for training a NEP via the ``nep``
    executable of the GPUMD package.

    Parameters
    ----------
    parameters
        dictionary containing the parameters to be set in the nep.in file;
        see `here <https://gpumd.org/nep/input_parameters/index.html>`__
        for an overview of these parameters
    structures
        list of structures to be included
    enforced_structures
        structures that _must_ be included in the training set, provided in the form
        of a list of indices that refer to the content of the ``structures`` parameter
    rootdir
        root directory in which to create the input files
    n_splits
        number of splits of the input structures in training and test sets that ought to be
        performed; by default no split will be done and all input structures will be used
        for training
    seed
        random number generator seed to be used; this ensures reproducability
    overwrite
        if True overwrite the content of ``rootdir`` if it exists
    """
    if exists(rootdir) and not overwrite:
        raise FileExistsError('Output directory exists.'
                              ' Set overwrite=True in order to override this behavior.')

    if n_splits is not None and (n_splits <= 0 or n_splits > len(structures)):
        raise ValueError(f'n_splits ({n_splits}) must be positive and'
                         f' must not exceed {len(structures)}.')

    rs = np.random.RandomState(seed)
    _prepare_training(parameters, structures, enforced_structures,
                      rootdir, n_splits, rs)


def _prepare_training(parameters: NamedTuple,
                      structures: List[Atoms],
                      enforced_structures: List[int],
                      rootdir: str,
                      n_splits: Optional[int],
                      rs: np.random.RandomState) -> None:
    """Prepares training and test sets and writes structural data as well as parameters files.

    See class-level docstring for documentation of parameters.
    """
    subdir = 'nepmodel_full'
    dirname = join_path(rootdir, subdir)
    makedirs(dirname, exist_ok=True)
    _write_structures(structures, dirname, list(set(range(len(structures)))), [0])
    write_nepfile(parameters, dirname)

    if n_splits is None:
        return

    kf = KFold(n_splits=n_splits, shuffle=True, random_state=rs)
    n_structures = len(structures)
    remaining_structures = list(set(range(n_structures)) - set(enforced_structures))
    for k, (train_selection, test_selection) in enumerate(kf.split(remaining_structures)):
        # append enforced structures at the end of the training set
        train_selection = list(train_selection)
        train_selection.extend(enforced_structures)

        # sanity check: make sure there is no overlap between train and test
        assert set(train_selection).intersection(set(test_selection)) == set(), \
            'Train and test set should not overlap'

        subdir = f'nepmodel_split{k+1}'
        dirname = join_path(rootdir, subdir)
        makedirs(dirname, exist_ok=True)
        _write_structures(structures, dirname, train_selection, test_selection)
        write_nepfile(parameters, dirname)


def _write_structures(structures: List[Atoms],
                      dirname: str,
                      train_selection: List[int],
                      test_selection: List[int]):
    """Writes structures in format readable by nep executable.

    See class-level docstring for documentation of parameters.
    """
    write_structures(
        join_path(dirname, 'train.xyz'),
        [s for k, s in enumerate(structures) if k in train_selection])
    write_structures(
        join_path(dirname, 'test.xyz'),
        [s for k, s in enumerate(structures) if k in test_selection])
