from pytest import approx
import numpy as np
import matplotlib.pyplot as plt
from optics.components import Polarimeter
import os
from lmfit import printfuncs


# def test_polarimeter_load():
#     filenames = []
#     ext = '.dat'
#     path = r'\\data.diamond.ac.uk\i06-1\data\2017\nt16891-1'
#     start_scan = 160171
#
#     for i in range(start_scan, start_scan + 8):
#         filenames.append(os.path.join(path, str(i) + ext))
#
#     pola = Polarimeter()
#     pola.load_scans(filenames)

# def test_polarimeter_reflectivity():
#     alpha = np.linspace(0, 315, 8)
#     beta = np.linspace(0, 360, 37)
#     pola = Polarimeter()
#     params = [1, 1, 0, 0, -45, 4, 0.002, 1, 1]
#     reflectivity = pola.calculate_reflectivity(alpha, beta, params)
#
#     assert 0 == 1


# def test_polarimeter_polarization():
#     filenames = []
#     ext = '.dat'
#     path = r'\\data.diamond.ac.uk\i06-1\data\2017\cm16752-2'
#     start_scan = 161008

#     for i in range(start_scan, start_scan + 8):
#         filenames.append(os.path.join(path, str(i) + ext))

#     pola = Polarimeter()
#     pola.load_scans(filenames)
#     polarization_result = pola.calculate_polarization()

#     params = polarization_result.params
#     average_data = pola.average_data
#     data = pola.data[:, 1, :]/pola.data[:, 3, :]

#     printfuncs.report_fit(params)

#     n_primary = pola.primary_angles.size
#     n_secondary = pola.secondary_angles_unique.size

#     parvals = params.valuesdict()
#     p = [parvals['s0'], parvals['s1'], parvals['s2'], parvals['s3'],
#          parvals['delta'], parvals['tp'], parvals['rp'], parvals['rp'], parvals['ts'], parvals['rs']]

#     fitted_data = np.reshape(pola.calculate_reflectivity(pola.secondary_angles_unique, pola.primary_angles, p),
#                              (n_primary, n_secondary))

#     fig = plt.figure()

#     for i in range(n_secondary):
#         ax = fig.add_subplot(2, 2, i+1)
#         ax.plot(pola.primary_angles, average_data[:, i])
#         ax.plot(pola.primary_angles, fitted_data[:, i])
#         ax.plot(pola.primary_angles, data[:, i])
#         ax.plot(pola.primary_angles, data[:, i + 4])

#     plt.show()
