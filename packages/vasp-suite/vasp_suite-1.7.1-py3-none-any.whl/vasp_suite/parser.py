"""
A module for parsing vasp output files.
"""

import os
import re

from .structure import Structure


class Parser(Structure):
    """
    Parent class for all parsers
    """

    def __init__(self, output_file):
        """
        Initializes the parser object.
        """
        # Initialize the structure object
        if not (os.path.exists('POSCAR')
                or os.path.exists('CONTCAR')):
            raise IOError("No POSCAR or CONTCAR file found.")
        super().from_poscar('POSCAR', inherit=True)

        self.output_file = output_file

    @property
    def read_lines(self):
        """
        Reads the lines from the output file
        """
        with open(self.output_file, 'r') as f:
            return f.readlines()

    def _make_generator(self, pattern):
        """
        Creates a generator object of lines matching the pattern
        """
        for line in self.read_lines:
            if pattern.match(line):
                yield line.strip().split()


class ParseOUTCAR(Parser):
    """
    Parses the OUTCAR file
    """

    # Patterns
    ext_pressure_pattern = re.compile(
            r'^\s+external\s+pressure\s+=\s+'
            )

    time_pattern = re.compile(
            r'^\s+Elapsed\s+time\s+'
            )

    def __init__(self, output_file='OUTCAR'):
        """
        Initializes the OUTCAR parser object.
        """
        super().__init__(output_file)

    def get_external_pressure(self):
        """
        Returns the external pressure
        """
        # UNITS: kB
        return [float(x[3]) for x in self._make_generator(
            self.ext_pressure_pattern)]

    def get_time(self):
        return [float(x[3]) for x in self._make_generator(
            self.time_pattern)]


class ParseOSZICAR(Parser):
    """
    Parses the OSZICAR file
    """

    energy_pattern = re.compile(
            r'^\s+([\-0-9\.]+)\s+F=\s+'
            )

    step_pattern = re.compile(
            r'[A-Z]{3}:\s+([\-0-9\.]+)\s+'
            )

    def __init__(self, ouput_file='OSZICAR'):
        """
        Initializes the OSZICAR parser object.
        """
        super().__init__(ouput_file)

    def get_energy(self):
        """
        returns the energy per atom
        """
        return [float(x[4]) for x in self._make_generator(
            self.energy_pattern)]

    def get_electronic_steps(self):
        """
        returns the number of electronic steps per
        ionic step
        """
        steps = [int(x[1]) for x in self._make_generator(
            self.step_pattern)]
        electronic_steps = []
        prev = 0
        for idx, step in enumerate(steps):
            if step == 1:
                electronic_steps.append(steps[prev:idx])
                prev = idx
        electronic_steps.append(steps[prev:])
        for list in electronic_steps:
            if len(list) < 1:
                electronic_steps.remove(list)
        return [max(x) for x in electronic_steps]
