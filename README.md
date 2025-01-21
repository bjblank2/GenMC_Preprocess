# GenMC_Preprocess

GenMC_Preprocess is a component of the Generalized Monte Carlo Toolkit for Magnetic Alloys (GenMC-MA). It is a Python-based preprocessing tool that facilitates the construction of lattice models by collating, verifying, and formatting data generated from DFT (Density Functional Theory) simulations. The processed data can then be used to parameterize models for simulating magnetic and alloy configurations. Currently, GenMC_Preprocess only supports VASP input files for the DFT dataset.

---

## Features

- **Collates DFT simulation results**: Automatically gathers results of DFT simulations into a single data file.
- **Formats data for lattice models**: Transforms DFT outputs into a compact format suitable for lattice model parameterization
- **Validates simulation results**: Identifies and flags incomplete or corrupt DFT results.
- **Analyze magnetic moment distribution**: Finds the distribution of magnetic moments for each constituent atomic species.

---

## Workflow

The general workflow for using GenMC_Preprocess involves the following steps:
1. Create a dataset from DFT simulations. 
    - Any model created with GenMC-MA is only as good as its dataset. In order to ensure the best possible mode, the dataset should include a diverse set of atomic and magnetic configurations. It is recommended that, for each unique POSCAR file in a dataset should be initialized with as many symmetrically unique configurations of magnetic moments as is practical.

    - The directory structure of the dataset should be organized as follows:

    |
    |_ Root Directory (Name)
	|
	|_ Any sub-directory organization (Optional)
		|
		|_ VASP Sumulation-1 Results (Name)
		|	|
		|	|_ POSCAR
		|	|_ CONTCAR
		|	|_ OUTCAR
		|
		|_ VASP Sumulation-2 Results (Name)
		|	|
		|	|_ POSCAR
		|	|_ CONTCAR
		|	|_ OUTCAR
		|...
   
   Each simulation results folder MUST contain at least a POSCAR, CONTCAR, and OUTCAR file. 
   Any additional VASP input or output files are welcome to remain in the folder but will be ignored. 
	
2. Format the "param_in" file.
   - An example "param_in" file is shown below:

```plaintext
root_dir: '/Users/Desktop/AlloyData'              # the top directory of your VASP data
do_compile_data: True                             # Choose whether or not to write the dataset to a single file
write_data: 'data_mag'                            # Path and name of your output dataset file
species: ['Ni', 'Mn', 'In']                       # Species in sequence as they appear in your POSCAR file
read_mag: True                                    # Flag to read magnetic moment from OUTCAR
use_spin_tol: True                                # Choose whether display spin as integers or total magnetic moment
spin_tol: [[0.2] , [3.0 , 2.0] , [ -1]]           # Spin tolerance here in the same sequence of species
do_mag_distrib: True                              # Choose whether or not to calculate magnetic moment distribution
write_mag_distrib: 'mag_distrib'                  # path and name of your magnetic distribution output file

   - The "spin_tol" option requires additional explanation. When the "use_spin_tol" flag is set to “True”, a spin tolerance method is used. In this case, magnetic moments read from the OUTCAR file are assigned integer values such as −1, 0, 1 or −1, 1. The mapping between the OUTCAR moments and the integer values and is provided by "spin_tol" using a tolarance vector. Each element in the vector represents how the tolarance is applied to the corisponding atomic species. In the example "param_in" file, the tolarance vector indicates that there are two allowable spin magnitudes for Ni atoms: 
	-- If ∥OUTCAR moment∥ > 0.2 then ∥spin∥ is set to 1 and its sign is set to sgn(OUTCAR moment)
	-- Otherwise ∥spin∥ is set to 0
The second element in the vector indicates that there are three allowable magnitudes for spins assigned to Mn atoms: 
        -- If ∥OUTCAR moment∥ > 3.0 then ∥spin∥ is set to 2 and its sign is set to sgn(OUTCAR moment)
	-- If ∥OUTCAR moment∥ < 3.0 and > 2.0 then ∥spin∥ is set to 1 and its sign is set to sgn(OUTCAR moment)
	-- Otherwise ∥spin∥ is set to 0.
For the third element in the vector a special value is used, -1. This indicates that, for all atoms of this type (in this case In) all spins are set to 0.0.

2. Run the GenMC_Preprocess Python script, which:
   - Compiles the DFT results into a single output file.
   - Applies user-defined tolerances for lattice constants and atomic positions.
   - Formats the magnetic and configurational data for lattice models.
3. Use the formatted data with GenMC_Fit for model parameterization.

---

## Example Parameter Input File

Below is an example parameter file for preprocessing a Ni2MnIn dataset:

```plaintext
root_dir: '/Users/Desktop/AlloyData'   # the top directory of your vasp data
do_compile_data: True                             # Choose whether or not to compile data dataset to a single file
write_data: 'data_mag'                            # Path and name of your output metadata file
species: ['Ni', 'Mn', 'In']                       # Species in sequence as they appear in your POSCAR file
read_mag: True                                    # Flag to read magnetic moment from OUTCAR
use_spin_tol: True                                # Choose whether display spin as integers or total magnetic moment
spin_tol: [[2,1], [0.4,0.2], [1.4,0.7]]           # Spin tolerance here in the same sequence of species
do_mag_distrib: True                              # Choose whether or not to calculate magnetic moment distribution
write_mag_distrib: 'mag_distrib'                  # path and name of your magnetic distribution output file

