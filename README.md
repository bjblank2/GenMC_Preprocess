# GenMC_Preprocess

GenMC_Preprocess is a component of the Generalized Monte Carlo Toolkit for Magnetic Alloys (GenMC-MA). It is a Python-based preprocessing tool that facilitates the construction of lattice models by collating, verifying, and formatting data generated from DFT (Density Functional Theory) simulations. The processed data can then be used to parameterize models for simulating magnetic and alloy configurations.

---

## Features

- **Collates DFT simulation results**: Automatically gathers results into a single data file.
- **Validates simulation results**: Identifies and flags incomplete or corrupt results.
- **Formats data for lattice models**: Transforms DFT outputs into a compact format suitable for lattice model parameterization.
- **Supports user-defined configurations**: Allows customization through a parameter input file.

---

## Workflow

The general workflow for using GenMC_Preprocess involves the following steps:
1. Create a dataset from DFT simulations. Each dataset must contain:
   - Atomic configurations (e.g., `POSCAR` files).
   - Magnetic initialization (`MAGMOM` tags in `INCAR` files).
   - Simulation results (`CONTCAR` and `OUTCAR` files).
2. Run the GenMC_Preprocess Python script, which:
   - Compiles the DFT results into a single output file.
   - Applies user-defined tolerances for lattice constants and atomic positions.
   - Formats the magnetic and configurational data for lattice models.
3. Use the formatted data with GenMC_Fit for model parameterization.

---

## Example Parameter Input File

Below is an example parameter file for preprocessing a Ni2MnIn dataset:

```plaintext
root_dir : '/Users/Ni2MnIn_data_set'
do_compile_datad : True
write_data : 'data_mag'
species : ['Ni', 'Mn', 'In']
lat_tol : [0.1, 0.1, 0.1]
pos_tol : [0.01, 0.01, 0.01]
read_mag : True
use_spin_tol : True
spin_tol : [[0.2], [3.0, 2.0], [-1]]
do_mag_distrib : True
write_mag_distrib : 'mag_distrib'
