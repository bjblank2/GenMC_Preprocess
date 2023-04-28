from pathlib import Path
import compile_vasp_data as cvd


# choose the mode here
do_this = "COMP_VASP"
# put the top directory with your vasp data here
root_dir = "/Users/tianyu/Desktop/Alloy/GenMC/GenMC_Preprocess/data_FeNiCr/533"
# define the location of your output file
vasp_data_file = '/Users/tianyu/Desktop/Alloy/GenMC/GenMC_Preprocess/data_FeNiCr/data1'
# this is the order that the post-processed data is reported
species = ['Fe', 'Ni', 'Cr']
# choose whether to use spin tolerance
use_spin_tol = True
# insert spin tolerance here in the same sequence of species
spin_tol = [0.5, 0.1, 0.3]

if do_this == "COMP_VASP":
    cvd.import_vasp_poscar(root_dir, vasp_data_file, species, use_spin_tol, spin_tol)
    print('\n')

if do_this == "FIND_NAMES":
    for filename in Path('D:/All_VASP').rglob('OUTCAR'):
        file = filename.open('r')
        outcar = file.readlines()
        for line in outcar:
            if "TOTEN" in line:
                enrg = line.split()[4]
                print(str(enrg)+", "+str(filename))
