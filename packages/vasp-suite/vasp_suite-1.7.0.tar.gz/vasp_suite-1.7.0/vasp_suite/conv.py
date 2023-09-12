"""
Convergence testing for vasp calculations
"""
import os
import shutil
import csv
import numpy as np

from .structure import Structure
from .parser import ParseOUTCAR, ParseOSZICAR
from .input import InputFileGenerator
from .core import generate_kpoints


def make_dirs(combinations):
    """
    Make directories for each combination of parameters
    and copy the input files into them
    """
    cwd = os.getcwd()

    for c in combinations:
        dir = '{}{}{}_{}'.format(c[0][0], c[0][1], c[0][2], c[1])
        if not os.path.exists(dir):
            os.makedirs(dir)
        shutil.copy(os.path.join(cwd, 'INCAR'), os.path.join(cwd, dir))
        shutil.copy(os.path.join(cwd, 'POTCAR'), os.path.join(cwd, dir))
        shutil.copy(os.path.join(cwd, 'POSCAR'), os.path.join(cwd, dir))
        os.chdir(dir)
        generate_kpoints(c[0])
        with open('INCAR', 'a') as f:
            f.write('ENCUT = {}\n'.format(c[1]))
        os.chdir(cwd)


def get_combinations(filename, max_encut):
    """
    Convergence test calculation set up
    """

    if os.path.splitext(filename)[1] == ".cif":
        filename = 'POSCAR'

    poscar = Structure.from_poscar(filename)

    # get the kpoint mesh and densities
    mesh, density = poscar.calculate_mesh()

    encut_values = poscar.calculate_encut(max_encut)

    combinations = [[x, y, z] for x, z in zip(mesh[:5], density[:5])
                    for y in encut_values]

    return combinations


def extract_data(combinations):
    """
    extracting data from the calculations
    for post processing
    """

    with open('conv.csv', 'w') as output_writer:
        output_writer_csv = csv.writer(output_writer, delimiter=',')

        output_writer_csv.writerow(
                ["Cutoff [eV]", "nk_1", "nk_2", "nk_3", "nk,red",
                 r"\rho_k [A^-3]", "E_0 [eV]", "p_ext [kbar]", "#SCF", "t [s]"]
                )

    for c in combinations:
        dir = '{}{}{}_{}'.format(c[0][0], c[0][1], c[0][2], c[1])
        outcar = ParseOUTCAR(os.path.join(dir, 'OUTCAR'))
        oszicar = ParseOSZICAR(os.path.join(dir, 'OSZICAR'))

        energy = oszicar.get_energy()
        ext_pressure = outcar.get_external_pressure()
        num_scf = oszicar.get_electronic_steps()
        time = outcar.get_time()
        n_k_red = np.prod(c[0])

        with open('conv.csv', 'a') as output_writer:
            output_writer_csv = csv.writer(output_writer, delimiter=',')
            output_writer_csv.writerow(
                    [c[1], c[0][0], c[0][1], c[0][2], str(n_k_red), c[2][0],
                     str(energy[0]), str(ext_pressure[0]),
                     str(num_scf[0]), str(time[0])]
                    )
