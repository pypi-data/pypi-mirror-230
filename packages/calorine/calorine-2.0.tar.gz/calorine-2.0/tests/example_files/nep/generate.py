import subprocess
from os.path import join as join_path

from ase.build import bulk
from ase.calculators.emt import EMT
from calorine.nep import setup_training


def nep_parameters():
    return dict(
        version=4,
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
        generation=1000,
    )


def get_structures():
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


def setup_parameters():
    return dict(train_fraction=0.5, seed=42, n_splits=None, overwrite=True)


version = '3.7'
dir = f'v{version}'
structures = get_structures()
params = setup_parameters()
nep = nep_parameters()
params['rootdir'] = dir
setup_training(nep, structures, **params)
path = join_path(params['rootdir'], 'nepmodel_full')
result = subprocess.run(
    [f'/home/elindgren/executables/gpumd-v{version}/nep'], capture_output=True, cwd=path
)
assert 'Finished running nep.' in str(result.stdout)
