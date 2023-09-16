import tempfile
import subprocess
import shutil


executable = '/home/elindgren/repos/NEP_CPU/src/a.out'
structure_dir = '../example_structures'
output_dir = '../example_output/'


def execute_model_in_temporary_directory(model, structure):
    with tempfile.TemporaryDirectory() as tmpdirname:
        print('created temporary directory', tmpdirname)
        # copy structure and model
        shutil.copy(f'{model}.txt', f'{tmpdirname}/nep.txt')
        shutil.copy(f'{structure_dir}/{structure}.in', f'{tmpdirname}/xyz.in')
        # Execute
        subprocess.Popen(['cat', 'xyz.in'], cwd=tmpdirname)
        subprocess.Popen([executable, '.'], cwd=tmpdirname).wait()
        # Copy back results
        shutil.copy(
            f'{tmpdirname}/descriptor.out',
            f'{output_dir}/{model}_{structure}_descriptor.out',
        )
        shutil.copy(
            f'{tmpdirname}/force_analytical.out',
            f'{output_dir}/{model}_{structure}_force.out',
        )
        shutil.copy(
            f'{tmpdirname}/virial.out', f'{output_dir}/{model}_{structure}_virial.out'
        )


models_and_structures = [
    ('C_NEP2_dummy', 'C_2atom'),
    ('CO_NEP2_dummy', 'CO_2atom'),
    ('CON_NEP2_dummy', 'CON_3atom'),
    ('PbTe_NEP2_dummy', 'PbTe_2atom'),
    ('nep3_v3.3.1_PbTe_Fan22', 'PbTe_2atom'),
    ('nep3_v3.3.1_PbTe_Fan22', 'PbTe_250atom'),
]


for model, structure in models_and_structures:
    execute_model_in_temporary_directory(model, structure)
