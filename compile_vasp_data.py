import numpy as np
from numpy.linalg import norm
import os
import copy


def cart_to_frac(cart_coord, basis):
    """
    transform from Cartesian coordinate to direct/fraction coordinate
    :param cart_coord: list in the format of [0, 0, 0]
    :param basis: list in the format of [[0.0, 0.0, 3.6], [0.0, 3.6, 0.0], [3.6, 0.0, 0.0]]
    :return: frac_coord
    """
    a1 = np.array(basis[0])
    a2 = np.array(basis[1])
    a3 = np.array(basis[2])
    cart_coord = np.array(cart_coord)
    trans_matr = np.vstack([a1, a2, a3]).T
    inv_matr = np.linalg.inv(trans_matr)
    frac_coord = np.matmul(inv_matr, cart_coord.T).T

    return list(frac_coord)


def apply_pbc(coord):
    """
    Apply periodic boundary conditions to a point
    :param coord: fraction coordinate for a given point
    :return: fraction coordinates using PBCs
    """
    pbc_coord = copy.deepcopy(coord)
    for i in range(3):
        pbc_coord[i] = np.around(pbc_coord[i], decimals=15) % 1

    return pbc_coord


def read_contcar_lat(contcar_lines):
    """
    read lattice constant and lattice vector from contcar file
    :param contcar_lines: read lines of contcar
    :return: lattice info from contcar/poscar
    """
    scale = float(contcar_lines[1])
    lat_const = []
    lat_vec = []
    lat_ang = []
    for i in range(2, 5):
        vec = np.array([float(x) for x in contcar_lines[i].split()]) * scale
        lat_vec.append(vec)
        lat_const.append(norm(vec))
    for i in range(3):
        j = (i + 1) % 3
        k = (i + 2) % 3
        cos_ = np.dot(lat_vec[j], lat_vec[k]) / (lat_const[j] * lat_const[k])
        lat_ang.append(np.arccos(np.clip(cos_, -1, 1)))

    return lat_const, lat_vec, lat_ang


def read_atat_pos(contcar_lines, species, lat_vec):
    """
        read species and composition from atat-formatted files
        :param contcar_lines: read lines of atat-formatted files
        :param species: users-defined species sequence
        :param lat_vec: lattice vector
        :return: species and position info from atat-formatted files
        """
    for i in range(len(contcar_lines)):
        if 'artesian' in contcar_lines[i] or 'irect' in contcar_lines[i]:
            pos_start = i + 1
    atom_sum = len(contcar_lines) - pos_start
    spec_list = [[]] * len(species)
    pos_list = [[]] * atom_sum
    seq = []
    for i in range(atom_sum):
        pnt = contcar_lines[pos_start + i].split()
        pos = []
        for j in range(3):
            pos.append(float(pnt[j]))
        if 'artesian' in contcar_lines[pos_start - 1]:
            pos = cart_to_frac(pos, lat_vec)
        pos = apply_pbc(pos)
        pos_list[i] = [pnt[3], pos]
        seq.append(pnt[3])
    pos_list.sort(key=lambda x: species.index(x[0]))
    spec_dict = {i: seq.count(i) for i in seq}
    for i in range(len(species)):
        for keys in spec_dict:
            if species[i] == keys:
                spec_list[i] = [spec_dict[keys], species[i]]
                break
            else:
                spec_list[i] = [0, species[i]]

    return spec_list, pos_list


def read_pos(contcar_lines, species, lat_vec):
    """
    read species and composition from contcar/poscar file
    :param species: users-defined species sequence
    :param contcar_lines: read lines of contcar
    :param lat_vec: lattice vector
    :return: species and position info from contcar/poscar
    """
    spec = contcar_lines[5].split()
    comp = contcar_lines[6].split()
    atom_sum = int(np.sum(np.array(comp, dtype=np.float64)))
    spec_list = [[]] * len(species)
    pos_list = [[]] * atom_sum
    seq = []
    for i in range(len(spec)):
        for j in range(int(comp[i])):
            seq.append(spec[i])
    for i in range(atom_sum):
        pnt = contcar_lines[8 + i].split()
        pos = []
        for j in range(3):
            pos.append(float(pnt[j]))
        if 'artesian' in contcar_lines[7]:
            pos = cart_to_frac(pos, lat_vec)
        pos = apply_pbc(pos)
        pos_list[i] = [seq[i], pos]
    pos_list.sort(key=lambda x: species.index(x[0]))
    spec_dict = {i: seq.count(i) for i in seq}
    for i in range(len(species)):
        for keys in spec_dict:
            if species[i] == keys:
                spec_list[i] = [spec_dict[keys], species[i]]
                break
            else:
                spec_list[i] = [0, species[i]]

    return spec_list, pos_list


def read_contcar_seq(contcar_lines):
    """
    :param contcar_lines: read lines of contcar
    :return: atomic sequence in contcar and outcar
    """
    spec = contcar_lines[5].split()
    comp = contcar_lines[6].split()
    seq = []
    for i in range(len(spec)):
        for j in range(int(comp[i])):
            seq.append(spec[i])

    return seq


def read_outcar(outcar_lines, seq_lines, species):
    """
    read energy and magnetism from outcar
    :param outcar_lines: read lines of outcar
    :param seq_lines: read lines of contcar
    :param species: users-defined species sequence
    :return: energy and magnetism
    """
    seq = read_contcar_seq(seq_lines)
    atom_num = len(seq)
    mag_list = [[]] * atom_num
    for i in range(len(outcar_lines)):
        if "TOTEN" in outcar_lines[i]:
            enrg = outcar_lines[i].split()
            enrg = float(enrg[4])
        if "magnetization (x)" in outcar_lines[i]:
            for j in range(atom_num):
                mag = outcar_lines[i + j + 4].split()
                mag_list[j] = [float(mag[4]), seq[j]]
    mag_list.sort(key=lambda x: species.index(x[1]))

    return enrg, mag_list


def import_vasp_poscar(root_dir, output_dir, species, use_spin_tol, spin_tol):
    output = open(output_dir, 'w')
    enrg_list = []
    for subdir, dirs, files in os.walk(root_dir):
        contcar_lines = []
        outcar_lines = []
        flag = 0
        for file in files:
            if 'POSCAR' in files and 'CONTCAR' in files and 'OUTCAR' in files:
                name = subdir.replace(root_dir, "")
                name = name.replace("/", "")
                if file == 'CONTCAR':
                    seq_file = open(subdir + '/' + file, 'r')
                    seq_lines = seq_file.readlines()
                    seq_file.close()
                if file == "POSCAR":
                    contcar = open(subdir + '/' + file, 'r')
                    contcar_lines = contcar.readlines()
                    contcar.close()
                    if len(contcar_lines) == 0:
                        print(subdir, ': empty structure file!')
                if file == "OUTCAR":
                    outcar = open(subdir + '/' + file, 'r')
                    outcar_lines = outcar.readlines()
                    outcar_len = len(outcar_lines)
                    for i in range(outcar_len):
                        if 'Elapsed time (sec):' in outcar_lines[i]:
                            flag = 1
                    if flag == 0:
                        print(subdir, ': unfinished job!')
                    outcar.close()
            else:
                print(subdir, ': no vasp files!')
        if len(contcar_lines) > 0 and len(outcar_lines) > 0 and len(seq_lines) > 0 and flag == 1:
            lat_const, lat_vec, lat_ang = read_contcar_lat(contcar_lines)
            if 'irect' in contcar_lines[7] or 'raction' in contcar_lines[7] or 'artesian' in contcar_lines[7]:
                spec_list, pos_list = read_pos(contcar_lines, species, lat_vec)
            else:
                spec_list, pos_list = read_atat_pos(contcar_lines, species, lat_vec)
            enrg, mag_list = read_outcar(outcar_lines, seq_lines, species)
            if use_spin_tol:
                for mag in mag_list:
                    if spin_tol[species.index(mag[1])] == 0:
                        mag[0] = 0
                    elif np.abs(mag[0]) < spin_tol[species.index(mag[1])]:
                        mag[0] = 0
                    else:
                        mag[0] = 1 * np.sign(mag[0])
            # start writing outputs
            output.write("# ")
            for i in range(len(species)):
                output.write(str(species[i]) + " ")
            output.write('\n')
            for i in range(len(spec_list)):
                output.write(str(spec_list[i][0]) + "\t")
            output_line = name + "\t" + str(enrg) + "\t" + \
                          str(lat_const[0]) + "\t" + str(lat_const[1]) + "\t" + str(lat_const[2]) + "\t" \
                          + str(lat_ang[0]) + "\t" + str(lat_ang[1]) + "\t" + str(lat_ang[2]) + "\n"
            output.write(output_line)
            output_line = str(lat_vec[0][0]) + "\t" + str(lat_vec[0][1]) + "\t" + str(lat_vec[0][2]) + "\n"
            output.write(output_line)
            output_line = str(lat_vec[1][0]) + "\t" + str(lat_vec[1][1]) + "\t" + str(lat_vec[1][2]) + "\n"
            output.write(output_line)
            output_line = str(lat_vec[2][0]) + "\t" + str(lat_vec[2][1]) + "\t" + str(lat_vec[2][2]) + "\n"
            output.write(output_line)
            for i in range(len(pos_list)):
                output_line = "\t" + str(i) + "\t" + str(species.index(pos_list[i][0])) + "\t" \
                              + str(mag_list[i][0]) + "\t" + str(pos_list[i][1][0]) + "\t" \
                              + str(pos_list[i][1][1]) + "\t" + str(pos_list[i][1][2]) + "\n"
                output.write(output_line)
    output.close()
