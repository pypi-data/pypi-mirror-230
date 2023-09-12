"""Diffraction grating module.

This module contains a class Grating to represent and describe the physical
properties and behaviour of a periodic ruled diffraction grating.
"""

from math import cos, sin, acos, asin, sqrt, pi
from optics.utilities.converter import Converter


class Grating:
    """Diffraction grating.

    This class describes the physical properties and
    behaviour of a periodic ruled diffraction grating.
    """
    def __init__(self, line_density=600, energy=250, cff=2, order=1):
        self._line_density = line_density
        self._energy = energy
        self._cff = cff
        self._order = order
        self._alpha = None
        self._beta = None
        # alpha and beta instance attributes set below
        self.compute_angles(line_density, energy, cff, order)

    @property
    def cff(self):
        """Fixed-focus constant."""
        return cos(self._beta*pi/180)/cos(self._alpha*pi/180)

    @cff.setter
    def cff(self, cff):
        self.compute_angles(self._line_density, self._energy, cff, self._order)
        self._cff = cff

    @property
    def energy(self):
        """Energy of diffracted light in eV."""
        wavelength = (sin(self._alpha*pi/180) +
                      sin(self._beta*pi/180))/(self._order*self._line_density*1000)

        if wavelength == 0:
            return 0

        return Converter.convert_energy_wavelength(wavelength)

    @energy.setter
    def energy(self, energy):
        self.compute_angles(self._line_density, energy, self._cff, self._order)
        self._energy = energy

    @property
    def order(self):
        """Order of diffraction."""
        return (sin(self._beta*pi/180) +
                sin(self._alpha*pi/180))/(self.wavelength()*self._line_density*1000)

    @order.setter
    def order(self, order):
        self.compute_angles(self._line_density, self._energy, self._cff, order)
        self._order = order

    @property
    def line_density(self):
        """Line density of grating in lines/mm."""
        return (sin(self._beta*pi/180) +
                sin(self._alpha*pi/180))/(self.wavelength()*self._order*1000)

    @line_density.setter
    def line_density(self, line_density):
        self.compute_angles(line_density, self._energy, self._cff, self._order)
        self._line_density = line_density

    @property
    def alpha(self):
        """Angle of incidence of light w.r.t. grating surface normal in degrees."""
        alpha = 90

        try:
            alpha = asin(self._order*self._line_density*1000*self.wavelength() -
                         sin(self._beta*pi/180))*180/pi
        except ValueError:
            print('Error: grating.alpha')

        return alpha

    @alpha.setter
    def alpha(self, alpha):
        try:
            u = self._order*self._line_density*1000*self.wavelength() - sin(alpha*pi/180)
            self._beta = asin(u)*180/pi
        except (ZeroDivisionError, ValueError):
            print('Error: grating.alpha.setter')

        self._alpha = alpha

    @property
    def beta(self):
        """Angle of diffraction of light w.r.t. grating surface normal in degrees."""
        beta = -90

        try:
            beta = asin(self._order*self._line_density*1000*self.wavelength() -
                        sin(self._alpha*pi/180))*180/pi
        except ValueError:
            print('Error: grating.beta')

        return beta

    @beta.setter
    def beta(self, beta):
        try:
            u = self._order*self._line_density*1000*self.wavelength() - sin(beta*pi/180)
            self._alpha = asin(u)*180/pi
        except (ZeroDivisionError, ValueError):
            print('Error: grating.beta.setter')

        self._beta = beta

    def set_angles(self, alpha, beta):
        """Set the angles of the indcident and diffracted light.

        In addition to setting the alpha and beta angles,
        the corresponding wavelength/energy of light and
        the cff value are also calculated.
        """
        wavelength = (sin(alpha*pi/180) + sin(beta*pi/180))/(self._line_density*1000*self._order)

        try:
            self._energy = Converter.convert_energy_wavelength(wavelength)
        except ZeroDivisionError:
            print('Error: grating.set_angles')

        self._alpha = alpha
        self._beta = beta
        self._cff = self.cff

    def wavelength(self):
        """Wavelength of light diffracted by the grating in nm."""
        return Converter.convert_energy_wavelength(self._energy)

    def compute_angles(self, line_density, energy, cff, order):
        """Set the incident and diffraction angles of the grating based
        on the line density of the grating, the energy of the incoming light,
        the desired cff value and the diffraction order.
        """
        wavelength = Converter.convert_energy_wavelength(energy)
        lambda_u = order*line_density*1000*wavelength/(1 - cff*cff)
        sin_alpha = lambda_u + sqrt(1 + lambda_u*lambda_u*cff*cff)
        self._alpha = asin(sin_alpha)*180/pi
        self._beta = -acos(cos(asin(sin_alpha))*cff)*180/pi
        return self._alpha, self._beta

    @staticmethod
    def compute_beta(alpha, line_density, energy, order):
        beta = 0

        try:
            wavelength = Converter.convert_energy_wavelength(energy)
            u = order*line_density*1000*wavelength - sin(alpha*pi/180)
            beta = asin(u)*180/pi
        except (ZeroDivisionError, ValueError):
            print('Error: grating.compute_beta')

        return beta
