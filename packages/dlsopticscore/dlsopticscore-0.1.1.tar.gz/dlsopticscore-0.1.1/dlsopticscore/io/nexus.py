"""nexus module.

This module contains a class Nexus for handling files in the Nexus (.nxs)
file format. Also handles .hdf files.
"""

import h5py
import numpy as np


class Nexus:
    """Nexus class.

    This class handles files in the Nexus (.nxs) and HDF (.hdf) formats.
    """
    def __init__(self, groupstoload=None, valuestoload=None,
                 basegroup='/entry1/instrument/{0}/{0}',
                 basevalue='/entry1/before_scan/{0}/{0}'):
        """Initialize the groups and values to load from a Nexus/HDF file.

        Args:
            groupstoload -- array of strings containing the data groups to load
                (default None)
            valuestoload -- array of strings containing the single values to
                load (default None)
            basegroup -- default formatted string for generating data groups
            basevalue -- default formatted string for generating value strings
        """
        self.groups_to_load = groupstoload
        self.values_to_load = valuestoload
        self.base_group = basegroup
        self.base_value = basevalue

    def load_data(self, filename):
        """Load data groups from specified filename."""
        f = h5py.File(filename, 'r')

        data = []

        for group in self.groups_to_load:
            data.append(np.asarray(f[group]))

        return np.transpose(np.asarray(data))

    def load_values(self, filename):
        """Load values from specified filename."""
        f = h5py.File(filename, 'r')

        values = []

        for value in self.values_to_load:
            values.append(f[value][()])

        return values

    def set_groups_from_base(self, entries):
        """Generate group strings from array of entry names."""
        groups = []

        for entry in entries:
            groups.append(self.base_group.format(entry))

        self.groups_to_load = groups

    def set_values_from_base(self, entries):
        """Generate value strings from array of entry names."""
        values = []

        for entry in entries:
            values.append(self.base_value.format(entry))

        self.values_to_load = values
