## Data Set Generation

With the exception of structure generation, such as generating SQS structures or structures with a user-defined degree of short-range order, the GenMC-MA workflow begins with building a data set of DFT simulations. For the purpose of constructing a lattice model, the initial data set must contain a diversity of atomic and magnetic configurations, and the configurations in the data set must span the intended composition space.

While GenMC-MA does not currently have the functionality to **automatically** generate a DFT data set, it provides a **tool** to assist in this process. This tool is designed to make the data set generation process more efficient by creating certain VASP [Kresse1993, Kresse1994, Kresse1996, Kresse1996a] inputs, such as `POSCAR` files and corresponding magnetic configurations.

When building effective models for complex magnetic alloys, manually generating configuration files can quickly become cumbersome due to the large amount of data required. GenMC-MA's **short range order** optimization algorithm enables users to automatically generate new configurations with a user-prescribed degree of short-range order, provided the systems are large enough for a Monte Carlo solver. (See section 3.3.4 for more details.)  
By contrast, for **small ordered systems** (around 16 atoms or fewer), you must still create the atomic configurations (`POSCAR`) and magnetic initialization (`MAGMOM` in `INCAR`) manually.

After all necessary input files are created, run your VASP simulations. GenMC-MA pulls simulation results from the `CONTCAR` and `OUTCAR` files. The outputs of each DFT simulation must be organized in **individual folders** under a common home directory. Each folder must include:

- A valid `POSCAR`
- A valid `CONTCAR`
- A valid `OUTCAR`

If any of these files are missing, corrupt, or incomplete, GenMC-MA will report the issue when you run the relevant code.

---

### Assumptions About Structures and Relaxations

When processing DFT results, GenMC-MA assumes a **user-defined crystal structure** with specific lattice sites. Data processing extracts information from relaxed DFT structures—identifying which atoms occupy which sites, as well as nearest neighbors. Common lattice models (cluster expansions, Ising-like models) typically **ignore exact inter-atomic distances**, because they assign energies based on coordination environments. Bond lengths factor in only insofar as local environment correlates with bond lengths.

However, for computing DFT configuration energies, you typically permit **full relaxations** of the lattice shape, atomic positions, and volume. This can shift atoms away from their initial high-symmetry arrangement. Within GenMC-MA:

- **POSCAR** defines your intended, “reference” sites,
- **CONTCAR** shows the final, relaxed structure.

To maintain a consistent phase or symmetry, a **tolerance** is applied to any deviations between `POSCAR` and `CONTCAR`. If a structure relaxes beyond this threshold, it will be excluded from the data set. We recommend testing different tolerances for convergence and stability.

Another consideration is the **shape** of each structure in the data set. GenMC-MA does **not** require every structure to be a supercell of the same unit cell, only that they map to the same **primitive cell** with minimal differences in inter-atomic distances. For instance, a primitive cell and a conventional cell can both be included in the data set, provided they represent equivalent local coordination environments.

---

## Preparing Data Sets with GenMC-MA — *GenMC_Preprocess*

Once you have constructed (and run) your DFT simulations, the next step in the GenMC-MA workflow is **data processing and re-formatting**. The tools for this step are found in the `GenMC_Preprocess` Python code, which:

1. **Collates** DFT simulation results into a single data file,  
2. **Identifies** incomplete or corrupt simulations, and  
3. **Formats** each simulation to be consistent with a lattice model representation (atom types, spin states, etc.).

The **collation and filtering** occur automatically when you run the `GenMC_Preprocess` script, while **formatting** requires a user-supplied `param_in` file. Below is an example `param_in` file for a Ni\(_2\)MnIn data set:

```yaml
root_dir: '/Users/Ni2MnIn_data set'
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
Line 1 (root_dir) specifies the home directory holding all DFT simulations.
Line 2 (do_compile_datad) states whether to create (or overwrite) a data set file.
Line 3 (write_data) is the output filename for the collated data.
Line 4 (species) lists all possible atomic species (order must match POSCAR).
lat_tol and pos_tol describe allowed deviations between POSCAR and CONTCAR for lattice constants and atom positions, respectively.
If magnetism is included in the model, set read_mag to True. Then the final atomic moments from OUTCAR are read and must be assigned to spin values. The user selects between:

Retaining raw DFT magnetic moments, or
Applying a moment cutoff (the “spin tolerance” method), which maps the DFT moment to an integer spin state.
This choice is made via the use_spin_tol flag. When True, the code expects a spin_tol list for each species:

-1 → All spins for that species are zero (e.g., a non-magnetic element).
0 → Assigns a uniform spin magnitude of 1 (sign from DFT).
Positive numbers → Define cutoff boundaries. For example, [3.0, 2.0] means:
Moment 
∣
𝑚
∣
>
3.0
∣m∣>3.0 ⇒ spin magnitude 2,
2.0
<
∣
𝑚
∣
≤
3.0
2.0<∣m∣≤3.0 ⇒ spin magnitude 1,
∣
𝑚
∣
≤
2.0
∣m∣≤2.0 ⇒ spin magnitude 0,
with sign set by the actual DFT moment (positive or negative).
Determining Moment Cutoffs
Selecting cutoffs is critical. The user is advised to test multiple tolerance schemes and observe how the resulting spin-lattice model behaves. To assist with this, GenMC_Preprocess can produce a “moment distribution” file (do_mag_distrib: True), which logs all final atomic moments. From that file, you can plot histograms (for instance, as shown below) to see the distribution of magnetic moments across your data set:



Here, we see three clusters of Mn moments at 0, ~2.8, and ~3.5 
𝜇
𝐵
μ 
B
​
 . The smaller cluster near 2.8 
𝜇
𝐵
μ 
B
​
  could be folded in with the main 3.5 
𝜇
𝐵
μ 
B
​
  peak, or considered a separate magnetic state.

Example Output from GenMC_Preprocess
When you run GenMC_Preprocess, it compiles each valid structure into a single output file. Below is an example for a single Ni
2
2
​
 MnIn simulation:

bash
Copy
# Ni Mn In
8  4  4  \Ni2MnIn\Mart\B0  -88.5581  5.2  5.2  5.2  1.5708  1.5708  1.5708
5.2 0  0
0  5.2  0
0  0  7.8
   0   0   1.0   0.25   0.25   0.25
   1   0   1.0   0.75   0.25   0.25
   2   0   1.0   0.25   0.75   0.25
   3   0   1.0   0.75   0.75   0.25
   4   0   1.0   0.25   0.25   0.75
   5   0   1.0   0.75   0.25   0.75
   6   0   1.0   0.25   0.75   0.75
   7   0   1.0   0.75   0.75   0.75
   8   1   1.0   0.5    0.0    0.0
   9   1   1.0   0.0    0.5    0.0
   10  1   1.0   0.5    0.0    0.5
   11  1   1.0   0.0    0.5    0.5
   12  2   0     0.0    0.0    0.0
   13  2   0     0.5    0.5    0.0
   14  2   0     0.0    0.0    0.5
   15  2   0     0.5    0.5    0.5
The first line lists the species (here, Ni, Mn, In).
The second line shows the number of each species, the directory path, the final relaxed energy (in eV), the lattice constants, and lattice angles (in radians).
The next three lines are the lattice vectors from the initial POSCAR.
The remaining lines list, for each atom:
Index (0-based),
Species (0 = Ni, 1 = Mn, 2 = In),
Assigned spin,
Fractional coordinates (from POSCAR).
All accepted structures are compiled in this manner, forming the data set input for GenMC_Fit, which subsequently constructs and fits the lattice model.
