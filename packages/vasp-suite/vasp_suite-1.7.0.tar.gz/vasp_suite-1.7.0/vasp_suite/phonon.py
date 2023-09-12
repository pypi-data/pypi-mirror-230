"""
Handles the automation of phonopy calculations.
"""

import os
import numpy as np
import socket

def disp_files():
    """
    Identifies the number of 'POSCAR-XXX' files in the current directory.
    """
    disp_files = [x for x in os.listdir()
                  if x.startswith('POSCAR-')]

    disp_files = [x.split('-')[1] for x in disp_files]
    disp_files = [int(x) for x in disp_files]

    return max(disp_files)


def check_config():
    """
    Checks if the config file exists.
    """
    if os.path.isfile(os.path.join(os.path.expanduser('~'),
                                   '.vasp_suite_configs/phonon.ini')):
        return True
    else:
        return False


def create_displacements(supercell):
    """
    Uses phonopy to create displacements.
    """

    os.system('phonopy -d --dim="{}"'.format((" ".join(map(str, supercell)))))
    print('Displacements created.')


class phonopy_submit():

    def __init__(self, cores, kpoints):
        self.cores = cores
        self.kpoints = kpoints
        if self.kpoints != [1, 1, 1]:
            self.vasp_type = 'vasp_std'
        else:
            self.vasp_type = 'vasp_gam'
        hostname = socket.gethostname()
        if 'csf3' in hostname:
            self.hostname = 'csf3'
            self.module = 'apps/intel-19.1/vasp/5.4.4'
            self.sub = 'qsub'
        elif 'csf4' in hostname:
            self.hostname = 'csf4'
            self.module = 'vasp/5.4.4-iomkl-2020.02'
            self.sub = 'sbatch'
        else:
            self.hostname = None
            self.sub = 'mpirun ...'

    def write_submit(self, disp):
        with open('submit.sh', 'w') as f:
            if self.hostname == 'csf3':
                f.write("#!/bin/bash --login \n")
                f.write("#$ -cwd \n")
                f.write("#$ -pe smp.pe {} \n".format(self.cores))
                f.write("#$ -N phonopy \n \n")
                f.write("module load {} \n \n".format(self.module))
            if self.hostname == 'csf4':
                f.write("#!/bin/bash --login \n")
                f.write("#SBATCH -p multicore \n")
                f.write("#SBATCH -n {} \n".format(self.cores))
                f.write("#SBATCH --job-name=phonopy \n \n")
                f.write("module load {} \n \n".format(self.module))

            f.write("echo 'Started running at `date`' \n \n")
            f.write("for f in $(ls POSCAR-{001..%03d}) \n" % disp)
            f.write("do \n")
            f.write('if [ -f "${f}" ] \n then \n')
            f.write('d="${f/POSCAR-/}" \n')
            f.write('if [ ! -d "${d}" ] && mkdir "${d}" \n then \n')
            f.write('cd "${d}" \n')
            f.write('cp "../INCAR" "../KPOINTS" "../POTCAR" . \n')
            f.write('mv "../${f}" "POSCAR" \n')
            f.write('mpirun -np {} {}_par '.format(self.cores, self.vasp_type) + '>../${d}.out \n')
            f.write('cd .. \n')
            f.write('fi \n')
            f.write('fi \n')
            f.write('done \n \n')
            f.write("echo 'Finished running at `date`' \n \n")

        os.system('chmod +x submit.sh')
        # print in green
        print('\033[92m' + "{} submit.sh".format("run " + self.sub) + '\033[0m')
