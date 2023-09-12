''' Input is a module which handles the genereation of input and submission files for VASP calculations. '''
# Impoting modules
import configparser as cp
import os
import socket
from .structure import Structure, get_extension


class InputFileGenerator(Structure):
    '''
    InputFileGenerator is a class which generates input files for VASP calculations.
    '''

    def __init__(self, filename: str, calculation: str):
        '''
        Initializes the class.
        '''
        ext = get_extension(filename)
        if ext == 'cif':
            super().from_cif(filename, inherit=True)
            self.write_poscar('POSCAR')
        else:
            super().from_poscar(filename, inherit=True)
        self.configuration = calculation

        hostname = socket.gethostname()
        if 'csf3' in hostname:
            self.pseudopotentials = '/opt/apps/apps/intel-19.1/vasp/5.4.4/pseudopotentials/potpaw_PBE.54'
            self.module = 'apps/intel-19.1/vasp/5.4.4'
        elif 'csf4' in hostname: 
            self.pseudopotentials = '/opt/software/RI/apps/VASP/5.4.4-iomkl-2020.02/pseudopotentials/potpaw_PBE.54'
            self.module = 'VASP/5.4.4-iomkl-2020.02'
        elif os.path.exists(
                os.path.join(
                    os.path.expanduser('~'),
                    '.vasp_suite_configs/host.ini')):
            config = cp.ConfigParser()
            config.read(os.path.join(os.path.expanduser('~'), '.vasp_suite_configs/host.ini'))
            try:
                self.pseudopotentials = os.path.join(
                        os.path.expanduser('~'), config['host']['pseudopotentials'])
                self.module = config['host']['module']
            except KeyError:
                print('''Create a host.ini file in ~/.vasp_suite_configs with the following format:
                [host]
                pseudopotentials = /path/to/pseudopotentials
                module = module_name''')
                raise KeyError(f'''No configuration found for {hostname}.''')
        else:
            raise Warning('Unable to generate POTCAR file. No configuration found for this host.')

    def generate_incar(self):
        config = cp.ConfigParser()
        input_file = os.path.join(os.path.expanduser('~'), '.vasp_suite_configs', f'''{self.configuration}.ini''')
        config.read(input_file)
        with open('INCAR', 'w') as f:
            for section in config.sections():
                for key in config[section]:
                    key = key.upper()
                    f.write(f'''{key} = {config[section][key]}\n''')

    def generate_potcar(self):
        pseudo = self.pseudopotentials
        potpaw = ['H', 'He', 'Li_sv', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na_pv', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K_sv', 'Ca_sv', 'Sc_sv', 'Ti_sv', 'V_sv', 'Cr_pv', 'Mn_pv', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga_d', 'Ge_d', 'As', 'Se', 'Br', 'Kr', 'Rb_sv', 'Sr_sv', 'Y_sv', 'Zr_sv', 'Nb_sv', 'Mo_sv', 'Tc_pv', 'Ru_pv', 'Rh_pv', 'Pd', 'Ag', 'Cd', 'In_d', 'Sn_d', 'Sb', 'Te', 'I', 'Xe', 'Cs_sv', 'Ba_sv', 'La', 'Ce_3', 'Nd_3', 'Pm_3', 'Sm_3', 'Eu_2', 'Gd_3', 'Tb_3', 'Dy_3', 'Ho_3', 'Er_3', 'Tm_3', 'Yb_2', 'Lu_3', 'Hf_pv', 'Ta_pv', 'W_sv', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl_d', 'Pb_d', 'Bi_d', 'Po_d', 'At', 'Rn', 'Fr_sv', 'Ra_sv', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm']
        atoms = self.atoms

        files = [x.split('_') for x in potpaw if x.split('_')[0] in atoms]
        for i in range(len(atoms)):
            for j in range(len(files)):
                if files[j][0] == atoms[i]:
                    files[j].append(i)
        files.sort(key=lambda x: x[-1])
        files = [x[:-1] for x in files]
        files = ['_'.join(x) for x in files]
        cwd = os.getcwd()

        with open('POTCAR', 'w') as f:
            os.system(f'''module load vasp''')
            os.chdir(pseudo)
            for file in files:
                os.chdir(str(file))
                with open('POTCAR', 'r') as g:
                    f.write(g.read())
                os.chdir(pseudo)
            os.chdir(cwd)
