# GenMC_Preprocess
# GenMC-MA: Data Set Generation and Preprocessing

This repository provides tools for generating and preprocessing *ab initio* data sets for use with **GenMC-MA**, a workflow designed to construct and parametrize lattice models for complex magnetic alloys. Below, we outline the process of data set generation, discuss how to handle relaxed atomic and magnetic configurations, and illustrate how to prepare these data using the **GenMC_Preprocess** script.

---

## 1. Overview

GenMC-MA facilitates building effective lattice models (such as cluster expansions or spin-lattice models) from density functional theory (DFT) data. In general, you will need:
1. A set of structural (POSCAR) and magnetic (MAGMOM) configurations for each composition of interest.
2. Corresponding VASP output files (CONTCAR, OUTCAR) for each configuration after running DFT.
3. A common directory structure to house simulation results.
4. A parameter file (`param_in`) to guide how GenMC_Preprocess collates and interprets your DFT results.

The **GenMC-MA** approach:
- Assumes that atomic and magnetic configurations are mapped to a user-defined lattice model.
- Requires that structural relaxations do not deviate too drastically from the intended symmetry (a user-defined tolerance is applied).
- Allows for the inclusion of magnetism by either preserving raw magnetic moments or mapping moments to discrete spin values.

---

## 2. Data Set Generation

With the exception of creating certain special structures (e.g., SQS or specific short-range order configurations), the **GenMC-MA** workflow starts by constructing a diverse data set of DFT simulations that span the desired composition range. While GenMC-MA does not currently automate the creation of new DFT jobs, it **does** provide tools to assist in generating:

- **POSCAR** files for atomic configurations.
- Corresponding magnetic configurations (through VASP’s `MAGMOM` tag in `INCAR`).

Because the accuracy of any lattice model depends on the variety and completeness of the data set, it is critical to ensure:
1. Sufficient diversity in the atomic arrangements (covering all relevant compositions).
2. Inclusion of any relevant magnetic configurations, ensuring a representative set of magnetic moments for each atomic species.

### 2.1 Short Range Order Generation

For systems large enough to support Monte Carlo (MC) solvers, **GenMC-MA** can automatically generate new structures with a user-defined degree of short range order. Smaller, ordered systems (fewer than ~16 atoms) will still likely require manually prepared `POSCAR` files and `MAGMOM` settings.

### 2.2 VASP Simulations and Directory Structure

After generating all input files, run your DFT simulations in VASP. 
- **GenMC-MA** requires a valid `POSCAR`, `CONTCAR`, and `OUTCAR` for each configuration.  
- These files should be stored in individual folders under a common home directory.

The code checks for missing, corrupt, or incomplete files upon data processing. 

### 2.3 Lattice Model Assumptions

**GenMC-MA** typically assumes a *fixed* underlying crystal structure with well-defined lattice sites. Full structural relaxations (lattice shape, atomic positions, and volume) are permissible, but:
- Large deviations from the intended lattice symmetry may invalidate the configuration for the model (determined via user-defined tolerances).
- Inter-atomic distances are not directly considered, as typical lattice or Ising models only rely on atomic coordination.

For each accepted structure, **GenMC-MA** will:
1. Read the final positions from both `POSCAR` (initial) and `CONTCAR` (relaxed).
2. Compare them against the expected ideal structure using user-defined tolerances.
3. Reject any simulation exceeding those tolerances (e.g., change of crystal symmetry).

---

## 3. Preparing Data Sets with **GenMC_Preprocess**

Once DFT calculations are complete and organized, you can use the **GenMC_Preprocess** Python script to:

1. **Collate** the results of all DFT simulations into a single, consolidated data file.
2. **Identify** and discard incomplete or corrupt simulations.
3. **Format** simulation data into a lattice model representation (atomic site, spin, etc.).

This behavior is largely automated, but a user-supplied parameter file `param_in` specifies important run-time options such as allowed tolerances and magnetism handling.

### 3.1 Example `param_in` File

Below is an example `param_in` file for a Ni\(_2\)MnIn data set. Lines and flags are explained in detail thereafter:

```yaml
root_dir: '/Users/Ni2MnIn_data_set'
do_compile_datad: True
write_data: 'data_mag'
species: ['Ni', 'Mn', 'In'] 
lat_tol: [0.1, 0.1, 0.1]
pos_tol: [0.01, 0.01, 0.01]
read_mag: True
use_spin_tol: True
spin_tol: [[0.2], [3.0, 2.0], [-1]]
do_mag_distrib: True
write_mag_distrib: 'mag_distrib'
