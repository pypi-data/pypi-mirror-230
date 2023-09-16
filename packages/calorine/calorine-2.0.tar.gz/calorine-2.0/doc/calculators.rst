.. index::
   single: Function reference; Calculators

ASE calculators
===============

:program:`calorine` provides two ASE calculators for NEP calculations, one that uses the GPU implementation and one that uses the CPU implementation of NEP.
For smaller calculations the CPU calculators is usually more performant.
For very large simulations and for comparison the GPU calculator can be useful as well.
         
.. currentmodule:: calorine.calculators

GPU calculator
--------------

.. autoclass:: GPUNEP
   :members: run_custom_md, set_atoms, set_directory, single_point_parameters, command

CPU calculator
--------------

.. autoclass:: CPUNEP
   :members: set_atoms
