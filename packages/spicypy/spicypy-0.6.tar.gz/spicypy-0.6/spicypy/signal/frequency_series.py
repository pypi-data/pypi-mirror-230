"""
Class extending functionality of :obj:`gwpy.frequencyseries.frequencyseries.FrequencySeries` from GWpy

Authors:
    | Artem Basalaev <artem[dot]basalaev[at]physik.uni-hamburg.de>
    | Christian Darsow-Fromm <cdarsowf[at]physnet.uni-hamburg.de>
    | Shreevathsa Chalathadka Subrahmanya <schalath[at]physnet.uni-hamburg.de>
"""
from warnings import warn
import gwpy.frequencyseries
import numpy as np
from astropy.units import UnitsError
from astropy import units as u


class FrequencySeries(gwpy.frequencyseries.FrequencySeries):
    """
    Class to model spectra of signals (frequency series), inherits from GWpy

    """

    def times_iomega(self, omega_exponent=1):
        """Differentiate or integrate spectrum wrt. time

        Parameters
        ----------
        omega_exponent : int
            Power of i*omega in multiplication factor, i.e. spectrum is multiplied by (i*omega)^omega_exponent.

            * values > 0 correspond to differentiation omega_exponent times,
            * values < 0 correspond to integration omega_exponent times.

        Returns
        -------
        FrequencySeries
            Integrate/differentiate frequency series.
        """
        if omega_exponent == 0:
            warn("Specified omega_exponent is 0. Returning as it is")
            return self
        omega = self.frequencies * 2 * np.pi
        dc_bin = False
        if omega[0] == 0.0:  # avoid potential divide by zero
            omega = omega[1:]
            dc_bin = True

        # let's first check if any of the values are complex
        if np.iscomplex(self.value).any():
            omega = (
                1j * omega
            )  # yes, there are complex values -  do it "properly" with i*omega
            # otherwise, ignore the i and apply real omega factor

        # calculate omega factor
        omega_pow = np.power(omega, omega_exponent)

        if dc_bin:
            omega_pow = np.insert(omega_pow, 0, 0.0)
        output = self * omega_pow
        # astropy mixes Hz and s. Manual correction is done below.
        for _ in range(abs(omega_exponent)):
            if omega_exponent > 0:
                output.override_unit(output.unit / u.Hz / u.s)
            else:
                output.override_unit(output.unit * u.Hz * u.s)
        return output

    def to_displacement(self):
        """Integrate the spectrum once or twice to convert to displacement.
        Input spectrum must have velocity or acceleration units.

        Parameters
        ----------

        Returns
        -------
        FrequencySeries
            Displacement frequency series.
        """

        # first check units - only velocity and acceleration can be converted to displacement
        original_units = ["m*s(-1)/Hz(1/2)", "m*s(-2)/Hz(1/2)"]
        omega_exponents = [
            -1,
            -2,
        ]  # possible exponents to use, depending on whether it is velocity or acceleration
        omega_exponent = None
        for i in range(len(omega_exponents)):
            try:
                self.unit.to(original_units[i])  # pylint: disable=no-member
            except UnitsError:
                continue  # could not convert to this unit, try with another one
            omega_exponent = omega_exponents[
                i
            ]  # converted to this unit - save omega_factor and stop the loop
            break

        if omega_exponent is None:
            raise ValueError(
                "Units of this FrequencySeries ",
                self.unit,
                " cannot be converted to displacement",
            )
        return self.times_iomega(omega_exponent)

    def to_velocity(self):
        """Integrate the spectrum once or differentiate once to convert to velocity.
        Input spectrum must have displacement or acceleration units.

        Parameters
        ----------

        Returns
        -------
        FrequencySeries
            Velocity frequency series.
        """

        # first check units - only displacement and acceleration can be converted to velocity
        original_units = ["m/Hz(1/2)", "m*s(-2)/Hz(1/2)"]
        omega_exponents = [
            1,
            -1,
        ]  # possible exponents to use, depending on whether it is displacement or acceleration
        omega_exponent = None
        for i in range(len(omega_exponents)):
            try:
                self.unit.to(original_units[i])  # pylint: disable=no-member
            except UnitsError:
                continue  # could not convert to this unit, try with another one
            omega_exponent = omega_exponents[
                i
            ]  # converted to this unit - save omega_factor and stop the loop
            break

        if omega_exponent is None:
            raise ValueError(
                "Units of this FrequencySeries ",
                self.unit,
                " cannot be converted to velocity",
            )
        return self.times_iomega(omega_exponent)

    def to_acceleration(self):
        """Differentiate the spectrum once or twice once to convert to acceleration.
        Input spectrum must have displacement or velocity units.

        Parameters
        ----------

        Returns
        -------
        FrequencySeries
            Acceleration frequency series.
        """

        # first check units - only displacement and velocity can be converted to acceleration
        original_units = ["m/Hz(1/2)", "m*s(-1)/Hz(1/2)"]
        omega_exponents = [
            2,
            1,
        ]  # possible exponents to use, depending on whether it is displacement or velocity
        omega_exponent = None
        for i in range(len(omega_exponents)):
            try:
                self.unit.to(original_units[i])  # pylint: disable=no-member
            except UnitsError:
                continue  # could not convert to this unit, try with another one
            omega_exponent = omega_exponents[
                i
            ]  # converted to this unit - save omega_factor and stop the loop
            break

        if omega_exponent is None:
            raise ValueError(
                "Units of this FrequencySeries ",
                self.unit,
                " cannot be converted to acceleration",
            )
        return self.times_iomega(omega_exponent)

    @property
    def is_asd(self):
        """Checks whether the input is ASD or not"""
        if self.unit == "Hz(1/2)":  # only possible for frequency ASD
            return True
        if self.unit == "1/Hz(1/2)":  # only possible for strain (unitless) ASD
            return True
        # let's assume it _is_ ASD, then if we do the following the frequency unit should cancel out
        test_unit = self.unit * u.Unit("Hz (1/2)")
        # now find out which units it had:
        bases = test_unit.decompose().bases
        # now try to force decompose this unit in base units from above _plus_ a frequency unit
        bases.append(u.Hz)
        if "Hz" in test_unit.decompose(bases=bases).bases:
            # as residual frquency unit is still present, not ASD
            return False
        # can be only ASD at this point
        return True

    @property
    def is_psd(self):
        """Checks whether the input is PSD or not"""
        if self.unit == "Hz":  # only possible for frequency PSD
            return True
        if self.unit == "1/Hz":  # only possible for strain (unitless) PSD
            return True
        test_unit = self.unit * u.Unit("Hz (1/2)")
        bases = test_unit.decompose().bases
        if len(bases) == 1 and "s" in bases:
            pass  # bypass for frequency ASD
        else:
            bases.append(u.Hz)
        if "Hz" in test_unit.decompose(bases=bases).bases:
            # as residual frquency unit is still present
            return True
        return False

    def rms(self, start_frequency=None):
        """Calculates the high-to-low RMS of the input spectrum.

        Parameters
        ----------
        start_frequency: float
            frequency to begin accumulating RMS (optional)

        Return
        ------
        rms: FrequencySeries
            High-to-low frequency cumulative RMS
        """
        rms = self.copy()

        # sanity check
        if (self.is_asd is False and self.is_psd is False) or (
            self.is_asd is True and self.is_psd is True
        ):
            raise ValueError(
                "Could not determine from units whether this FrequencySeries is ASD or PSD, cannot calculate RMS!"
            )
        # at this point we know whether it's PSD or ASD (and it can be nothing else)
        # if PSD, first take square root and then proceed with calculation for ASD
        if self.is_psd:
            rms = np.sqrt(rms)
        if start_frequency is not None:
            n_cut = np.where(self.frequencies.value > start_frequency)[0][0]
            rms = self[0:n_cut]

        bin_widths = np.diff(rms.frequencies)
        bin_widths = np.append(bin_widths[0], bin_widths)
        rms = np.sqrt(np.flip(np.cumsum(np.flip(rms * rms * bin_widths))))

        return rms
