# Import argparse
import argparse
from textwrap import dedent
import numpy as np
import os

# Import Modules
from . import core
from . import phonon
from . import conv
from . import input

# Create the wrapper funstions

def generate_input_func(args):
    '''
    Wrapper function for the generate_input function

    parameters
    ----------
    filename : str
    config_file : file

    Returns
    -------
    INCAR : file
    '''
    core.generate_input(
        filename=args.poscar,
        calculation=args.config_file,
            )

def calculate_kpoints_func(args):
    '''
    Wrapper function for the calculate_kpoints function

    parameters
    ----------
    filename : str

    Returns
    -------
    KPOINT mesh : int 
    '''
    core.calculate_kpoints(
            filename=args.poscar,
            )

def generate_kpoints_func(args):
    '''
    Wrapper function for the generate_kpoints function 

    parameters
    ----------
    mesh : int 

    Returns
    -------
    KPOINTS : file
    '''
    core.generate_kpoints(
            mesh=args.mesh,
            )


def generate_supercell_func(args):
    '''
    Wrapper function for the generate_supercell function

    parameters
    ----------
    expansion : list
    poscar : str

    Returns
    -------
    POSCAR : file
    '''
    core.generate_supercell(
            expansion=np.array(args.expansion, dtype=int),
            filename=args.poscar,
            )

def generate_job_func(args):
    '''
    Wrapper function for the generate_job function 

    parameters
    ----------
    title : str
    cores : int
    vasp_type : str

    Returns
    -------
    job.sh : file
    '''
    core.generate_job(
            title=args.title,
            cores=args.cores,
            vasp_type=args.vasp_type,
            conv=False
            )

def start_up_func(args):
    '''
    Wrapper function for the start_up function

    parameters
    ----------
    None

    Returns
    -------
    configuration files : file
    '''
    core.create_input_configurations()

def dope_structure_func(args):
    '''
    Wrapper function for the dope_structure function

    parameters
    ----------
    filename : str
    dopant : str
    replace : str
    instances : int

    Returns
    -------
    POSCARs : file
    '''
    core.dope_structure(
        filename=args.poscar,
        dopant=args.dopant,
        replace=args.replace,
        instances=args.instances,
        )

def generate_defect_func(args): 
    '''
    Wrapper function for the generate_defect function

    parameters
    ----------
    filename : str
    site : str
    instances : int

    Returns
    -------
    POSCAR : file
    '''
    core.generate_defect(
            filename=args.poscar,
            site=args.site,
            instances=args.instances,
            )


def find_molecule_func(args):
    '''
    Wrapper function for the asymmetric_unit function

    parameters
    ----------
    filename : str
    atom : str
    bond_max : float

    Returns
    -------
    POSCAR : file
    '''
    core.molecule(
            filename=args.poscar,
            atom=args.atom,
            bond_max=args.bond_max,
            )


def convert_cif_func(args):
    '''
    Wrapper function for the convert_cif function

    parameters
    ----------
    filename : str

    Returns
    -------
    POSCAR : file
    '''
    core.convert_cif(
            filename=args.filename,
            )

def phonon_calc(args):
    '''
    wrapper function for phonon calculation

    parameters
    ----------
    supercell : list
    mesh : list
    encut : int
    cores : int
    bec : bool

    Returns
    -------
    None
    '''
    supercell = args.supercell
    mesh = args.mesh
    encut = args.encut
    cores = args.cores
    bec = args.bec

# Check if the config file exists
    if not phonon.check_config():
        raise ValueError('No config file found, please run the start_up command')

# Generate the input files
    core.generate_input('POSCAR', 'phonon')
    core.generate_kpoints(mesh=mesh)

    with open('INCAR', 'a') as f:
        f.write('ENCUT = {}\n'.format(str(encut)))
        if bec:
            f.write('LEPSILON = .TRUE.')

# Create displacements
    phonon.create_displacements(supercell)

# get the number of displacements
    disp = phonon.disp_files()

# Generate the job file
    job = phonon.phonopy_submit(cores, mesh)
    job.write_submit(disp)


def convergence_func(args):
    """
    Wrapper function for the convergence function

    parameters
    ----------
    poscar : str
        The structure file to be used, POSCAR or CIF
    cores : int
        The number of cores to be used
    """
    if not os.path.exists(args.poscar):
        raise FileNotFoundError('{} does not exist'.format(args.poscar))

    input_file = input.InputFileGenerator(filename=args.poscar, calculation=args.scf_type)
    input_file.generate_incar()
    input_file.generate_potcar()

    combinations = conv.get_combinations(
            filename=args.poscar, max_encut=args.max_encut + 50
            )
    conv.make_dirs(combinations)
    core.generate_job(title='conv', cores=args.cores, vasp_type='vasp_std', conv=True)


def convergence_csv_func(args):
    """
    Wrapper function for the convergence_csv function

    parameters
    ----------
    poscar : str
        The structure file to be used, POSCAR
    """
    combinations = conv.get_combinations(
            filename=args.poscar, max_encut=args.max_encut + 50)
    conv.extract_data(combinations)


def coord_sphere_func(args):
    """
    Wrapper function for the coord_sphere function

    parameters
    ----------
    poscar : str
        The structure file to be used, POSCAR
    atom : str
        The atom to be used
    bond_max : float
        The maximum bond length
    coordination_number : int
        The number of coordination spheres to be found: (1, 2)
    """
    if not os.path.exists(args.poscar):
        raise FileNotFoundError('{} does not exist'.format(args.poscar))

    if args.coordination_number not in [1, 2]:
        # print in green
        print('\033[92m' + 'coordination_number must be 1 or 2' + '\033[0m')
        print('\033[92m' + 'coordination_number set to 1' + '\033[0m')
        args.coordination_number = 1

    core.coord_sphere(
            filename=args.poscar,
            atom=args.atom,
            bond_max=args.bond_max,
            sphere_num=args.coordination_number,
            )


def read_args(arg_list=None):
    '''Reads the command line arguments'''
    parser = argparse.ArgumentParser(
            prog='vasp_suite',
            description=dedent(
                '''
                ---------------------------------------------------
                                                  
                      A suite of tools for VASP calculations      

                ---------------------------------------------------
                
                Available programmes:
                    vasp_suite generate_input ...
                    vasp_suite generate_job ...
                    vasp_suite calculate_kpoints ...
                    vasp_suite generate_kpoints ...
                    vasp_suite generate_supercell ...
                    vasp_suite convert_cif ...
                    vasp_suite set_up ...
                    vasp_suite dope_structure ...
                    vasp_suite generate_defect ...
                    vasp_suite find_molecule ...
                    vasp_suite phonon_calc ...
                    vasp_suite convergence ...
                    vasp_suite convergence_csv ...
                    vasp_suite coordination_sphere ...
                '''
                ),
            epilog=dedent(
                '''
                To display options for a specific programme, use vasp_suite <programme> -h
                '''
                ),
            formatter_class=argparse.RawDescriptionHelpFormatter
            )

    # Subparsers
    subparsers = parser.add_subparsers(dest='prog')

    gen_inp = subparsers.add_parser(
            'generate_input',
            description=dedent(
                '''
                Generation of INCAR and POTCAR files for VASP calculations.
                '''
                ),
            formatter_class=argparse.RawDescriptionHelpFormatter
            )

    gen_inp.set_defaults(func=generate_input_func)

    gen_inp.add_argument(
            '--config_file',
            help=dedent(
                """
                The configuration file for the input generation.

                Example:

                Inside ~/.vasp_suite_templates '.ini' configuration files are 
                stored. To perform a relaxation caluclation using the relaxation.ini 
                template, use the following command:

                "vasp_suite generate_input relaxation"
                """
                )
            )

    gen_inp.add_argument(
            '--poscar',
            help=dedent(
                '''
                The name of the structure file.
                '''
                ),
            )

    gen_job = subparsers.add_parser(
        'generate_job',
        formatter_class=argparse.RawDescriptionHelpFormatter
        )

    gen_job.set_defaults(func=generate_job_func)

    gen_job.add_argument(
        '--title',
        help='The title of the job'
        )

    gen_job.add_argument(
        '--cores',
        help='The number of cores to use',
        type=int,
        )

    gen_job.add_argument(
        '--vasp_type',
        help=dedent(
            '''
            The VASP programme you widh to use:

                - vasp_std

                - vasp_gam
            '''
            ),
        )

    calc_kpoints = subparsers.add_parser(
        'calculate_kpoints',
        formatter_class=argparse.RawDescriptionHelpFormatter
        )

    calc_kpoints.set_defaults(func=calculate_kpoints_func)

    calc_kpoints.add_argument(
            '--poscar',
            help=dedent(
                '''
                The name of the structure file.
                '''
                ),
            )

    gen_kpoints = subparsers.add_parser(
        'generate_kpoints',
        formatter_class=argparse.RawDescriptionHelpFormatter
        )

    gen_kpoints.set_defaults(func=generate_kpoints_func)

    gen_kpoints.add_argument(
        '--mesh',
        nargs=3,
        help=dedent(
            '''
            The mesh to use for the kpoints file.
            command line arguments are written in the form:
            a b c
            '''
            )
        )

    gen_supercell = subparsers.add_parser(
        'generate_supercell',
        formatter_class=argparse.RawDescriptionHelpFormatter
        )

    gen_supercell.set_defaults(func=generate_supercell_func)

    gen_supercell.add_argument(
        '--expansion',
        nargs=3,
        help=dedent(
            '''
            The expansion vector for the supercell, a b c
            '''
            ),
        )

    gen_supercell.add_argument(
            '--poscar',
            help=dedent(
                '''
                The name of the structure file
                '''
                ),
            )

    start_up = subparsers.add_parser(
        'set_up',
        formatter_class=argparse.RawDescriptionHelpFormatter
        )

    start_up.set_defaults(func=start_up_func)

    dope_struct = subparsers.add_parser(
        'dope_structure',
        formatter_class=argparse.RawDescriptionHelpFormatter
        )

    dope_struct.set_defaults(func=dope_structure_func)

    dope_struct.add_argument(
        '--poscar',
        help='The name of the structure file',
        )

    dope_struct.add_argument(
            '--dopant',
            help='The element to dope the structure with',
            )

    dope_struct.add_argument(
            '--replace',
            help='The element to replace',
            )

    dope_struct.add_argument(
            '--instances',
            help='The number of instances of the dopant to add',
            type=int,
            )

    gen_defect = subparsers.add_parser(
        'generate_defect',
        formatter_class=argparse.RawDescriptionHelpFormatter
        )

    gen_defect.set_defaults(func=generate_defect_func)

    gen_defect.add_argument(
            '--poscar',
            help='The name of the structure file',
            )

    gen_defect.add_argument(
            '--site',
            help='The name of the atom to remove',
            )

    gen_defect.add_argument(
            '--instances',
            help='The number of instances of defect',
            type=int,
            )

    asym = subparsers.add_parser(
        'find_molecule',
        formatter_class=argparse.RawDescriptionHelpFormatter
        )

    asym.set_defaults(func=find_molecule_func)

    asym.add_argument(
            '--poscar',
            help='The name of the structure file',
            )

    asym.add_argument(
            '--atom',
            help='The name of the spin centre in the molecular crystal',
            )

    asym.add_argument(
            '--bond_max',
            help='The maximum bond length/ Å',
            type=float,
            default=2.5,
            )

    cif = subparsers.add_parser(
            'convert_cif',
            formatter_class=argparse.RawDescriptionHelpFormatter
            )

    cif.set_defaults(func=convert_cif_func)

    cif.add_argument(
            '--filename',
            help='The name of the .CIF file',
            )

    phonon = subparsers.add_parser(
            'phonon_calc',
            formatter_class=argparse.RawDescriptionHelpFormatter
            )

    phonon.set_defaults(func=phonon_calc)

    phonon.add_argument(
            '--mesh',
            help='The mesh to use for the phonon calculation',
            nargs=3,
            type=int,
            )

    phonon.add_argument(
            '--cores',
            help='The number of cores to use for the phonon calculation',
            type=int,
            )

    phonon.add_argument(
            '--encut',
            help='The energy cutoff for the phonon calculation',
            type=int,
            )

    phonon.add_argument(
            '--supercell', '-s',
            help='The supercell to use for the phonon calculation',
            nargs=3,
            type=int,
            default=[1, 1, 1],
            )

    phonon.add_argument(
            '--bec',
            help='Calculate the Born effective charges',
            action='store_true',
            )

    conv = subparsers.add_parser(
            "convergence",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            )

    conv.set_defaults(func=convergence_func)

    conv.add_argument(
            '--poscar',
            help='The name of the POSCAR file',
            )

    conv.add_argument(
            '--cores',
            help='The number of cores to use for the calculation',
            type=int,
            )

    conv.add_argument(
            '--max_encut',
            help='The maximum energy cutoff to test',
            type=int,
            default=1000,
            )

    conv.add_argument(
            '--scf_type',
            help='The config file for the scf calculation. Default is scf with VDW',
            type=str,
            default='scf',
            )

    conv_ext = subparsers.add_parser(
            "convergence_csv",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            )

    conv_ext.set_defaults(func=convergence_csv_func)

    conv_ext.add_argument(
            '--poscar',
            help='The name of the POSCAR file',
            )

    conv_ext.add_argument(
            '--max_encut',
            help='The maximum energy cutoff that has been tested',
            type=int,
            default=1000,
            )

    cd_sphere = subparsers.add_parser(
            "coordination_sphere",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            )

    cd_sphere.set_defaults(func=coord_sphere_func)

    cd_sphere.add_argument(
            '--poscar',
            help='The name of the POSCAR file',
            )

    cd_sphere.add_argument(
            '--atom',
            help='The name of the atom to find the coordination sphere of, e.g. "Dy1"',
            )

    cd_sphere.add_argument(
            '--bond_max',
            help='The maximum bond length/ Å',
            type=float,
            default=2.5,
            )

    cd_sphere.add_argument(
            '--coordination_number',
            help='The coordination sphere number to find (1 or 2)',
            type=int,
            )

    # Parse the ArgumentParser
    parser.set_defaults(func=lambda args: parser.print_help())
    args = parser.parse_known_args(arg_list)

    # Select programme 
    if args in ['generate_input, generate_job, calculate_kpoints, generate_kpoints, generate_supercell, start_up, dope_structure, generate_defect, asymmetric_unit, ewald, plot_potential, convert_cif']:
        args.func(args)
    else:
        args = parser.parse_args(arg_list)
        args.func(args)


def main():
    read_args()
