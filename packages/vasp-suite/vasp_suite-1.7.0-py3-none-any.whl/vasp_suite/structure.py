'''
A module for the Structure class. Structure will perform operations structure data files.
'''
# Imports
import re
import os
import numpy as np
import scipy as sp
import h5py
from functools import wraps
from time import perf_counter
from ase import io


def timer(func):
    '''
    A decorator function to time functions.
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = perf_counter()
        print(f'Running {func.__name__}...')
        func(*args, *kwargs)
        end = perf_counter()
        print(f"Time elapsed: {end - start}")
    return wrapper


class Structure:
    '''
    A class of functions for manipulating structure data files.
    '''

    @classmethod
    def from_poscar(cls, filename, inherit=False):
        '''
        Reads and formats a .vasp, POSCAR or CONTCAR file.

        Parameters
        ----------
        filename : str

        Returns
        -------
        Structure object
        '''
        with open(filename) as f:
            data = f.readlines()
        data = [x.strip().split() for x in data]

        cls.name: str = data[0]
        cls.scale: float = float(data[1][0])
        cls.av: np.ndarray = np.array(data[2:5], dtype=float)
        cls.atoms: list = data[5]
        cls.natoms: list = [int(x) for x in data[6]]
        cls._N: int = sum(cls.natoms)
        cls._type: str = data[7][0].lower()
        cls.coords: np.ndarray = np.array(data[8: 8 + cls._N], dtype=float)

        cls.cart_coords = cls.coords @ cls.av

        # Calculate reciprocal lattice vectors
        a1, a2, a3 = cls.av
        b1 = 2 * np.pi * np.cross(a2, a3) / (a1@np.cross(a2, a3))
        b2 = 2 * np.pi * np.cross(a3, a1) / (a2@np.cross(a3, a1))
        b3 = 2 * np.pi * np.cross(a1, a2) / (a3@np.cross(a1, a2))
        cls.bv: np.ndarray = np.array([b1, b2, b3])

        # Generate atom list
        atom_list = [f'{symbol} '*num
                     for symbol, num in zip(cls.atoms, cls.natoms)]

        atom_list = ' '.join(atom_list).split()
        cls._atom_list = atom_list

        # calculate the volume of the unit cell
        cls.V = np.dot(a1, np.cross(a2, a3))

        if inherit:
            return cls
        else:
            return cls()

    @classmethod
    def from_cif(cls, filename, inherit=False):
        '''
        Reads a .cif file and initializes it into the structure class.

        Parameters
        ----------
        filename : str

        Returns
        -------
        Structure object
        '''
        data = io.read(filename, format='cif')
        cls.name = data.get_chemical_formula()
        cls.scale = 1
        cls.av = data.cell.array
        cls._atom_list = data.get_chemical_symbols()
        cls._N = len(cls._atom_list)
        cls._type = 'direct'
        coords = data.get_scaled_positions()

        # convert atom list into atoms and natoms
        coords = np.hstack((np.array(cls._atom_list).reshape(-1, 1), coords))
        coords = coords[coords[:, 0].argsort()]
        cls._atom_list = list(coords[:, 0])
        cls.coords = np.array(coords[:, 1:], dtype=float)
        atoms = list(set(cls._atom_list))
        atoms.sort()
        natoms = [cls._atom_list.count(x) for x in atoms]
        cls.atoms = atoms
        cls.natoms = natoms

        cls.cart_coords = cls.coords @ cls.av

        # Calculate reciprocal lattice vectors
        a1, a2, a3 = cls.av
        b1 = 2 * np.pi * np.cross(a2, a3) / (a1@np.cross(a2, a3))
        b2 = 2 * np.pi * np.cross(a3, a1) / (a2@np.cross(a3, a1))
        b3 = 2 * np.pi * np.cross(a1, a2) / (a3@np.cross(a1, a2))
        cls.bv: np.ndarray = np.array([b1, b2, b3])

        # calculate the volume of the unit cell
        cls.V = np.dot(a1, np.cross(a2, a3))

        if inherit:
            return cls
        else:
            return cls()

    @classmethod
    def from_h5(cls, filename, inherit=False):
        '''
        Reads a .h5 file and initializes it into the structure class.

        Parameters
        ----------
        filename : str

        Returns
        -------
        Structure object
        '''
        with h5py.File(filename, 'r') as f:
            data = {key: f[key][()] for key in f.keys()}

        cls.name = data['name']
        cls.scale = data['scale']
        cls.av = data['lattice vectors']
        cls.bv = data['reciprocal lattice vectors']
        cls.atoms = data['atoms']
        cls.natoms = data['natoms']
        cls._type = data['type']
        cls.coords = data['coords']
        cls.cart_coords = data['cart coords']
        cls._atom_list = data['atom list']

        if inherit:
            return cls
        else:
            return cls()

    @property
    def get_name(self):
        '''
        Getter for name
        '''
        print(f'Name: {self.name}')
        return self.name

    @get_name.setter
    def rename(self, new_name: str):
        '''
        Setter for name
        '''
        print(f'Name changed from "{self.name}" to "{new_name}"')
        self.name = new_name

    @get_name.deleter
    def delete_name(self):
        '''
        Deleter for name
        '''
        print(f'Name "{self.name}" deleted')
        del self.name

    @property
    def as_dict(self) -> dict:
        '''
        Returns a dictionary of the structure.
        '''
        return {'name': self.name,
                'scale': self.scale,
                'lattice vectors': self.av,
                'reciprocal lattice vectors': self.bv,
                'volume': self.V,
                'atoms': self.atoms,
                'natoms': self.natoms,
                'atom list': self._atom_list,
                'type': self._type,
                'cart coords': self.cart_coords,
                'coords': self.coords}

    def generate_supercell(self, n: list) -> None:
        '''
        Creates a supercell of size n1 x n2 x n3.

        Parameters
        ----------
        n : list
            Expansion factor for each lattice vector.

        Returns
        -------
        None
        '''
        coords = self.coords
        av = self.av
        self.orig_av = av
        atom_list = self._atom_list

        _n1 = list(range(n[0]))
        _n2 = list(range(n[1]))
        _n3 = list(range(n[2]))
        _n = np.array([[_n1[i], _n2[j], _n3[k]]
                       for i in range(len(_n1))
                       for j in range(len(_n2))
                       for k in range(len(_n3))])

        coords = np.array([coord + _n[i]
                           for i in range(len(_n))
                           for coord in coords], dtype=float)

        for i in range(len(coords)):
            coords[i, 0] = coords[i, 0] / n[0]
            coords[i, 1] = coords[i, 1] / n[1]
            coords[i, 2] = coords[i, 2] / n[2]

        av[0], av[1], av[2] = av[0] * n[0], av[1] * n[1], av[2] * n[2]
        atom_list = [atom_list] * np.prod(n)
        atom_list = np.array(atom_list).flatten()

        self.coords = coords
        self.av = av
        self._atom_list = atom_list

    def reorder_supercell(self):
        """
        Reorders the supercell to be written in POSCAR form
        """
        coords = self.coords
        _atom_list = self._atom_list
        coords = np.concatenate((_atom_list.reshape(-1, 1), coords), axis=1)
        coords = coords[coords[:, 0].argsort()]
        self.coords = coords[:, 1:]
        self._atom_list = coords[:, 0]

        atoms = []
        for i in self._atom_list:
            if i not in atoms:
                atoms.append(i)
        natoms = [list(self._atom_list).count(i) for i in atoms]

        self.atoms = atoms
        self.natoms = natoms

    def shift_coords(self, vector: np.ndarray, basis):
        """
        Shifts the structure by a constant vector.

        Parameters
        ----------
        vector : np.ndarray
            Vector to shift the structure by.
        basis : str
            Basis to shift the structure in. Either 'cart' or 'frac'.

        Returns
        -------
        None
        """
        if basis == 'C':
            self.cart_coords += vector

        if basis == 'F':
            self.coords += vector
            self.coords %= 1

    def calculate_mesh(self) -> np.ndarray:
        '''
        Calculates K-point mesh.
        '''
        kpoint_mesh = []
        kspacing_min, kspacing_max = 0.05, 0.5
        av = self.av
        bv = self.bv
        bv_norm = np.array([np.linalg.norm(x) for x in bv], dtype=float)

        temp = [(i, norm) for i, norm in enumerate(bv_norm)]
        temp.sort(key=lambda x: x[1], reverse=True)

        i1, i2, i3 = [i for i, _ in temp]

        # Calculate the number of subdivisions N1, N2, N3 in the reciprocal lattice vectors 
        N_max = max(1, int(np.ceil(bv_norm[i1] / kspacing_min)))
        N_min = max(1, int(np.ceil(bv_norm[i1] / kspacing_max)))

        for n1 in range(N_min, N_max):
            min_spacing = bv_norm[i1] / n1
            if np.fabs(bv_norm[i2] - bv_norm[i1]) < 1e-5:
                n2 = n1
            else:
                n2 = int(np.ceil(bv_norm[i2] / min_spacing))
                n2 = max(n2, 1)

            if np.fabs(bv_norm[i3] - bv_norm[i2]) < 1e-5:
                n3 = n2
            else:
                n3 = int(np.ceil(bv_norm[i3] / min_spacing))
                n3 = max(n3, 1)

            if bv_norm[i2] / n2 < kspacing_max and bv_norm[i3] / n3 < kspacing_max:
                mesh = np.array([None, None, None])

            mesh[i1], mesh[i2], mesh[i3] = n1, n2, n3 
            kpoint_mesh.append(mesh)

        # calculate kpoint density
        volume = np.linalg.det(bv)
        density = np.array([[np.prod(mesh) / volume] for mesh in kpoint_mesh], dtype=float)

        return np.array(kpoint_mesh, dtype=int), density

    def calculate_encut(self, max_encut) -> np.ndarray:
        '''
        Calculates possible ENCUT values to test for convergence.
        '''
        # check if POTCAR file exits
        if not os.path.isfile('POTCAR'):
            raise Warning('POTCAR file not found. Please generate POTCAR file first.')

        def generate_enmax(lines: list):
            for line in lines:
                if 'ENMAX' in line:
                    yield float(line.split('=')[1].split(';')[0])

        with open('POTCAR', 'r') as f:
            lines = f.readlines()
        enmax = generate_enmax(lines)
        encut = max(list(enmax)) * 1.3
        encut = round(encut / 50) * 50
        encut_list = [x for x in range(encut, max_encut, 50)]
        self.encut = encut_list
        return np.array(encut_list)

    def get_index(self, atom: str):
        '''
        finds the index of the supplied atom in the coords
        and then returns the index of the atom in the atom_list

        Parameters
        ----------
        atom : str
            atom to find the index of

        Returns
        -------
        index : int
        '''
        atom = re.split(r'(\d+)', atom)
        for ind, symb in enumerate(self.atoms):
            if symb == atom[0]:
                atom_index = ind

        return atom_index

    def get_vector(self, idx: int, atom: str):
        """
        Returns the vector that shifts the atom to the origin.

        Parameters
        ----------
        idx : int
            Index of the atom in the coords.
        atom : str
            Atom to shift to the origin.

        Returns
        -------
        vector : np.ndarray
        """
        _prev = np.sum(self.natoms[:idx])
        location = int(_prev) + int(atom[1]) - 1
        return - self.coords[location]

    def write_xyz(self, filename):
        '''
        Writes an xyz file

        Parameters
        ----------
        filename : str
            Name of the file to write to.

        Returns
        -------
        None
        '''
        coords = self.cart_coords
        atom_list = self._atom_list

        with open(filename, 'w') as f:
            f.write(f'{len(coords)}\n\n')
            for i in range(len(coords)):
                f.write('{}\t{:.10f}\t{:.10f}\t{:.10f}\n'.format(
                    atom_list[i], coords[i, 0], coords[i, 1], coords[i, 2]))

    def write_poscar(self, filename):
        '''
        Writes POSCAR file.

        Parameters
        ----------
        filename : str

        Returns
        -------
        None
        '''
        self.coords = np.array(self.coords, dtype=float)
        with open(filename, 'w') as f:
            f.write('{}\n'.format(' '.join(self.name)))
            f.write('  {}\n'.format(self.scale))
            f.write('\t{:.10f}\t{:.10f}\t{:.10f}\n'.format(*self.av[0]))
            f.write('\t{:.10f}\t{:.10f}\t{:.10f}\n'.format(*self.av[1]))
            f.write('\t{:.10f}\t{:.10f}\t{:.10f}\n'.format(*self.av[2]))
            f.write('  {}\n'.format(' '.join(self.atoms)))
            f.write('   {}\n'.format(' '.join([str(x) for x in self.natoms])))
            f.write('{}\n'.format(self._type))
            for x in self.coords:
                f.write('  {:.10f}\t{:.10f}\t{:.10f}\n'.format(*x))


class Dope(Structure):
    """
    Class for doping structures.

    Parameters
    ----------
    Structure : Structure
    """

    def __init__(self, filename: str, dopant: str,
                 replace: str, instances: int):
        '''
        Initializes the DOPE class

        Parameters
        ----------
        filename : str
            Name of the file to read from.
        dopant : str
            Name of the dopant to add.
        replace : str
            Name of the atom to replace.
        instances : int
            Number of instances of the dopant to add.

        Returns
        -------
        None
        '''
        extension = get_extension(filename)
        if extension == 'cif':
            super().from_cif(filename, inherit=True)
        elif extension == 'vasp':
            super().from_poscar(filename, inherit=True)
        elif extension == 'h5' or extension == 'hdf5':
            super().from_h5(filename, inherit=True)
        else:
            raise ValueError(f'Extension {extension} not found.')

        self.dopant = dopant
        self.replace = replace
        self.instances = instances

    def Symbol_coords(self) -> np.ndarray:
        '''
        Returns the symbol and coordinates of the atoms in the structure.

        Returns
        -------
        coords : np.ndarray
        '''
        return np.hstack((np.array(self._atom_list).reshape(-1, 1), self.coords))

    def _replace_atom(self, coords) -> np.ndarray:
        '''
        Replaces the atom in the structure with the dopant in all possible locations.

        Parameters
        ----------
        coords : np.ndarray

        Returns
        -------
        coords : np.ndarray
        '''

        # validate replace atom
        if self.replace not in self.atoms:
            raise ValueError(f'Atom {self.replace} not found in structure.')

        structures = []
        temp_coords = coords.copy()
        prev_index = None
        for i in range(len(coords)):
            if coords[i][0] == self.replace and i != prev_index:
                temp_coords[i][0] = self.dopant
                prev_index = i
                structures.append(temp_coords)
                temp_coords = coords.copy()

        return np.array(structures)

    @timer
    def Generate_structure(self) -> np.ndarray:
        '''
        Generate the doped structures with a given number of 
        doped sites.

        Returns
        -------
        structures : np.ndarray
        '''
        structures = self._replace_atom(self.Symbol_coords())
        # transform structures into one array of structures
        instances = self.instances

        if instances == 1:
            pass
        else:
            for _ in range(instances-1):
                for i in range(len(structures)):
                    _temp = self._replace_atom(structures[i])
                    structures = np.vstack((structures, _temp))
                    structures = np.unique(structures, axis=0)

        # remove duplicarte structures
        structures = np.array([x for x in structures
                               if np.count_nonzero(
                                   x[:, 0] == self.dopant) == instances])
        structures = np.unique(structures, axis=0)
        for i in range(len(structures)):
            structures[i] = structures[i][structures[i][:, 0].argsort()]

        self._structures = structures
        print(f'Number of structures found = {len(structures)}')

    def Create_defect(self):
        '''
        Creates defects in the stucture

        Returns
        -------
        None
        '''
        structures = []
        for structure in self._structures:
            for i in range(len(structure)):
                try:
                    if structure[i][0] == self.dopant:
                        structure = np.delete(structure, i, axis=0)
                        structures.append(structure)
                except:
                    pass

        self._structures = np.array(structures)

    def write_poscars(self) -> None:
        '''
        Writes the doped structures to POSCAR files.
        '''
        structures = self._structures

        for i in range(len(structures)):
            atom_list = structures[i][:, 0]
            self.atoms, counts = np.unique(atom_list, return_counts=True)
            self.natoms = np.array([str(x) for x in counts])
            self.coords = structures[i][:, 1:]
            self.write_poscar('POSCAR-{}'.format(i+1))


class Rotate(Structure):
    '''
    A class for rotating structures.

    Parameters
    ----------
    Structure : Structure
    '''

    def __init__(self, filename: str, axis: str, angle: float):
        '''
        Initializes the Rotate class.
        '''
        extension = get_extension(filename)
        if extension == 'cif':
            super().from_cif(filename, inherit=True)
        elif extension == 'vasp':
            super().from_poscar(filename, inherit=True)
        elif extension == 'h5' or extension == 'hdf5':
            super().from_h5(filename, inherit=True)
        else:
            raise ValueError(f'Extension {extension} not found.')
        self.filename = filename
        self.axis = axis
        self.angle = angle
        self.Rx = np.array([
            [1, 0, 0],
            [0, np.cos(angle), -np.sin(angle)],
            [0, np.sin(angle), np.cos(angle)]
            ])
        self.Ry = np.array([
            [np.cos(angle), 0, np.sin(angle)],
            [0, 1, 0],
            [-np.sin(angle), 0, np.cos(angle)]
            ])
        self.Rz = np.array([
            [np.cos(angle), -np.sin(angle), 0],
            [np.sin(angle), np.cos(angle), 0],
            [0, 0, 1]
            ])

    def translate(self) -> None:
        """
        Translates the structure to the origin.
        """
        # find the centre
        coords = self.coords
        centre = np.mean(coords, axis=0)
        # translate the structure to the origin
        self.coords -= centre
        self.rotate_coords()
        self.coords = self.coords + centre

    def rotate_coords(self) -> None:
        '''
        Rotates the structure.
        '''
        # Rotate coordinates
        coords = self.coords
        if self.axis == 'x':
            self.coords = coords @ self.Rx
            # self.av = self._s.av @ self.Rx
        elif self.axis == 'y':
            self.coords = coords @ self.Ry
            # self.av = self._s.av @ self.Ry
        elif self.axis == 'z':
            self.coords = coords @ self.Rz
            # self.av = self._s.av @ self.Rz
        else:
            raise ValueError(f'Axis {self.axis} not found.')


class Molecule(Structure):
    '''
    A class for creating asymmetric units from a molecular crystal POSCAR file.

    Parameters
    ----------
    Stucture : Structure
    '''

    def __init__(self,
                 filename: str,
                 atom: str,
                 bond_max: float,
                 ):
        '''
        Initializes the Asymmetric_unit class.
        '''
        extension = get_extension(filename)
        if extension == 'cif':
            super().from_cif(filename, inherit=True)
        elif extension == 'vasp':
            super().from_poscar(filename, inherit=True)
        elif extension == 'h5' or extension == 'hdf5':
            super().from_h5(filename, inherit=True)
        else:
            raise ValueError(f'Extension {extension} not found.')
        self.atom = atom
        self.bond_max = bond_max

    def translate(self) -> None:
        '''
        Performs a translation and expansion to ensure a
        whole molecule is included.
        '''
        idx = self.get_index(self.atom)
        atom_symb = re.split(r'(\d+)', self.atom)
        self.vector = self.get_vector(idx, atom_symb)
        self.shift_coords(self.vector, basis='F')
        self.generate_supercell([2, 2, 2])
        self.vector = np.array([-.5, -.5, -.5])
        self.coords += self.vector
        self.cart_coords = self.coords @ self.av

    def origin_index(self) -> int:
        '''
        Finds the index of the origin atom.
        '''
        for ind, val in enumerate(self.coords):
            if np.allclose(val, [0, 0, 0]):
                return ind

    def nearest_neighbours(self, coords: np.ndarray, point: np.ndarray,
                            bond_max: float) -> np.ndarray:
        """
        Uses a KDTree to find the nearest neighbours of a point.

        Parameters
        ----------
        coords : np.ndarray
            The coordinates of the atoms.
        point : np.ndarray
            The central index coordinates.
        bond_max : float
            The maximum bond length.

        Returns
        -------
        coords : np.ndarray
            The coordinates of the nearest neighbours.
        """
        neighbours = sp.spatial.KDTree(coords[:, 1:], leafsize=10,
                                       compact_nodes=True, balanced_tree=True)
        dist, ind = neighbours.query(point, k=10)
        ind = [ind[i] for i in range(len(ind)) if dist[i] < bond_max]
        coords = np.array([coords[i] for i in ind])
        return coords

    @timer
    def find_molecule(self) -> None:
        '''
        Finds a molecule within a molecular crsytal structure.
        '''
        self.translate()
        atom_list = np.array(self._atom_list).reshape(-1, 1)
        origin = self.origin_index()
        coords = np.concatenate((atom_list, self.cart_coords), axis=1)

        asymm_unit = np.array([coords[origin]])
        while True:
            total_coords = []
            for i in asymm_unit:
                if not i[0] == 'H':
                    temp = self.nearest_neighbours(coords, i[1:],
                                                   self.bond_max)
                    for i in range(len(temp)):
                        total_coords.append(temp[i])
            total_coords = np.array(total_coords)
            total_coords = np.unique(total_coords, axis=0)
            if len(total_coords) == len(asymm_unit):
                break
            else:
                asymm_unit = total_coords

        self.cart_coords = np.array(asymm_unit[:, 1:], dtype=float)
        self._atom_list = asymm_unit[:, 0]
        self.write_xyz('molecule.xyz')

    @timer
    def get_coordination_sphere(self, coordination_sphere: int):
        """
        Finds the specified coordination sphere of a contiuous crystaline
        structure.

        Parameters
        ----------
        coordination_sphere : int
            The coordination sphere to find.
        """
        self.translate()
        coords = np.concatenate((np.array(self._atom_list).reshape(-1, 1),
                                 self.cart_coords), axis=1)
        sphere_coords = np.array(
                [coords[self.origin_index()]],
                )

        sphere_coords = np.concatenate(
                (sphere_coords, self.nearest_neighbours(coords, sphere_coords[0][1:], self.bond_max)),
                axis=0)
        sphere_coords = np.unique(sphere_coords, axis=0)

        if coordination_sphere == 1:
            self.cart_coords = np.array(sphere_coords[:, 1:], dtype=float)
            self._atom_list = sphere_coords[:, 0]
            self.write_xyz('coordination_sphere.xyz')
            return

        for atom in sphere_coords:
            sphere_coords = np.concatenate(
                    (sphere_coords, self.nearest_neighbours(coords, atom[1:], self.bond_max)),
                    axis=0)
            sphere_coords = np.unique(sphere_coords, axis=0)

        self.cart_coords = np.array(sphere_coords[:, 1:], dtype=float)
        self._atom_list = sphere_coords[:, 0]
        self.write_xyz('coordination_sphere.xyz')
        return


def get_extension(filename):
    """
    Gets the extension of a file.

    Parameters
    ----------
    filename : str
        The filename.

    Returns
    -------
    file_type: str
        The file extension.
    """
    parseable = ['cif', 'vasp', 'h5', 'hdf5']
    try:
        file_type = filename.split('.')[-1]
        if file_type not in parseable:
            raise ValueError('File type {} not supported.'.format(file_type))
        return file_type

    except:
        return 'vasp'
