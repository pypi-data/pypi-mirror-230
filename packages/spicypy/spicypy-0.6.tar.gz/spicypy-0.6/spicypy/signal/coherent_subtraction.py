"""
===============
Coherent subtraction (Huddle test in presence of signals)
===============

| Modified for Spicypy by Artem Basalaev <artem[dot]basalaev[at]physik.uni-hamburg.de>
| Reviewed by Christian Darsow-Fromm <cdarsowf[at]physnet.uni-hamburg.de>

Original description:

An attempt to make mccs in Python. We generalise this to support cross spectral
densities, something I assert is useful.

Although I only, properly, understand an alternative method for doing this
procedure that suffers from poor behaviour with non-linearly independent noise
sources. Alternatively I know that mccs works, and the community is happy with
its performance - so I will copy its functionality.

| Authors: Nathan A. Holland, Pooya Saffarieh, Brian Lantz, Conor Mow-Lowry
| Contact: nholland@nikhef.nl
| Date: 2022-05-20

Improvements to make:
    - Error checking needs to be improved
    - Support for more than 1 dimension in <x> and <y> data, and more than 2 dimensions for <ref> data - this was too hard for me to devise on the first programming of this function
    - Adjusted scaling factor for first bin (DC bin)
    - Better scaling factor for more than 1 ref. channel
    - Add warning for rank issues in lstsq
    - Return warning when input data is too small for a given average length

Major Difference from mccs2 in matlab:
    - We don't put zero in the first bin (DC)
    - For even number of data points here it returns n/2 + 1 rather than n/2

Pending important tests:
    - Non-hermitian signals.
    - Other window function rather than Hann and Rectangular.

"""

import numpy as np
from scipy.linalg import lstsq
from scipy.fft import fft, rfft, fftfreq, rfftfreq

from gwpy.timeseries import TimeSeriesDict

from spicypy.signal.spectral import (
    AveragingParameters,
    daniell_rearrange_fft,
    daniell_average,
)


def coherent_subtraction(*args, **kwargs):
    """Coherent subtraction of reference time series from test time series (typical use case: Huddle test)

    Parameters
    ----------
    args : `tuple`
        timeseries: `TimeSeries`
            input time series (if only one specified, calculates PSD)
        other: `TimeSeries`, optional
            second input time series
        reference: list or  `TimeSeriesDict`
            reference time series
    kwargs : `dict`
        additional arguments for Daniell method averaging

    Returns
    -------
    CSD : FrequencySeries
        residual spectrum (either CSD for two test inputs, of PSD for one)
    """

    try:
        test1, reference = args
        test2 = test1
    except ValueError:
        test1, test2, reference = args

    reference_list = reference
    if isinstance(reference, TimeSeriesDict):
        reference_list = []
        for channel in reference.keys():
            reference_list.append(reference[channel])
    elif not isinstance(reference, list):
        raise TypeError(
            "only TimeSeriesDict or list of TimeSeries are supported types for reference time series"
        )

    cs = CoherentSubtraction(test1, test2, reference_list, **kwargs)
    # process input arguments
    cs.check_inputs()
    # calculate FFTs for all inputs
    cs.prepare_ffts()
    # perform coherent subtraction
    cs.subtract()
    # average frequency bins, construct and normalize CSD, return
    return cs.average_CSD()


class CoherentSubtraction:  # pylint: disable=too-many-instance-attributes
    """
    Class performing coherent subtraction in frequency domain
    """

    def __init__(self, test1, test2, reference, **kwargs):
        """Init method for coherent subtraction

        Parameters
        ----------
        test1: `TimeSeries`
            input time series (if only one specified, calculates PSD)
        test2: `TimeSeries`, optional
            second input time series
        reference: list or  `TimeSeriesDict`
            reference time series
        kwargs : `dict`
            additional arguments for Daniell method averaging
        """
        self.test1 = test1
        self.test2 = test2
        self.reference = reference
        self.kwargs = kwargs

        # and set some defaults
        self.is_onesided = True
        self.detrend = "constant"
        self.ap = None
        self.test1_fft = None
        self.test2_fft = None
        self.reference_fft = None
        self.frq = None
        self.CSD = None
        self.bin_widths = None

    def check_inputs(self):
        """Check input arguments for coherent subtraction. Daniell-averaging-method-specific arguments are checked by `AveragingParameters` class."""
        # make a list of all other inputs and compare values to test1
        inputs_list = self.reference + [self.test1, self.test2]
        sample_rate = self.test1.sample_rate.value
        epoch = self.test1.epoch
        is_onesided = True

        for input_time_series in inputs_list:
            if len(input_time_series) != len(self.test1):
                raise ValueError(
                    "All time series must have the same length (number of samples)!"
                )
            if input_time_series.sample_rate.value != sample_rate:
                raise ValueError("All time series must have the same sampling rate!")
            if (
                input_time_series.epoch is not None
                and epoch is not None
                and input_time_series.epoch != epoch
            ):
                raise ValueError(
                    "All time series must be aligned in time (same time_series.epoch)!"
                )
            if np.iscomplexobj(input_time_series.value):
                is_onesided = (
                    False  # if any inputs are complex, will have two-sided fft
                )

        self.detrend = self.kwargs.pop("detrend", "constant")
        if self.detrend != "constant" and self.detrend != "linear":
            raise NotImplementedError(
                "Can only apply 'constant' and 'linear' detrend to time series"
            )

        # get parameters for Daniell method
        self.ap = AveragingParameters(sample_rate, len(self.test1), **self.kwargs)
        if len(self.reference) >= self.ap.number_averages // 2 + 1:
            raise ValueError(
                "For coherent subtraction to work, number of references must be <= number_averages // 2 + 1."
                "Try to increase `number_averages` value"
            )
        self.ap.is_onesided = is_onesided

    def prepare_ffts(self):
        """Detrend time series and calculate FFTs. Then rearrange ffts for Daniell averaging methods using `daniell_rearrange_fft` function."""
        # one-sided or two-sided fft
        if self.ap.is_onesided:
            fft_func = rfft
            fftfreq_func = rfftfreq
        else:
            fft_func = fft
            fftfreq_func = fftfreq

        # detrend time series, apply window, and perform fft (full length of time series is used, no segmenting)
        test1_fft = fft_func(
            self.test1.detrend(self.detrend).value * self.ap.win, self.ap.nfft
        )
        test2_fft = fft_func(
            self.test2.detrend(self.detrend).value * self.ap.win, self.ap.nfft
        )
        reference_fft = []
        for ref in self.reference:
            reference_fft.append(
                fft_func(ref.detrend(self.detrend).value * self.ap.win, self.ap.nfft)
            )

        # calculate corresponding frequencies
        frq = fftfreq_func(self.ap.nfft, 1.0 / self.ap.sample_rate)

        # now rearrange ffts according to Daniell method
        self.frq, self.test1_fft, self.ap = daniell_rearrange_fft(
            frq, test1_fft, self.ap
        )
        _, self.test2_fft, _ = daniell_rearrange_fft(frq, test2_fft, self.ap)
        self.reference_fft = []
        for ref_fft in reference_fft:
            _, fft_rearranged, _ = daniell_rearrange_fft(frq, ref_fft, self.ap)
            self.reference_fft.append(fft_rearranged)

    def subtract(self):
        """Perform coherent subtraction in frequency domain. Main method of the algorithm"""
        # perform coherent subtraction
        n_samples = len(self.test1_fft)
        number_reference_channels = len(self.reference_fft)
        self.CSD = np.full(n_samples, np.nan, dtype=complex)
        edges, self.bin_widths = self.ap.window_edges(self.CSD)
        left_edge = 0
        # do least square fit in each bin
        for right_edge in edges:
            test1_bin = self.test1_fft[left_edge:right_edge]
            test2_bin = self.test2_fft[left_edge:right_edge]
            ref_bin = np.zeros(
                [len(test1_bin), number_reference_channels], dtype=complex
            )

            # temporarily store references in another array to rearrange (see below)
            ref_tmp_bin = []
            for ref_fft in self.reference_fft:
                ref_tmp_bin.append(ref_fft[left_edge:right_edge])
            # Swap element indices for matrix operations on the next step to work
            # turns [[ref1_f1, ref1_f2, ref1_f3], [ref2_f1, ref2_f2, ref2_f3]]
            # to [[ref1_f1, ref2_f1] [ref1_f2, ref2_f2], [ref1_f3, ref2_f3]]
            for t in range(len(test1_bin)):
                for k in range(number_reference_channels):
                    ref_bin[t][k] = ref_tmp_bin[k][t]

            # turns [test1_f1, test1_f2, test1_f3]
            # to [[test1_f1], [test1_f2], [test1_f3]]
            test1_bin = test1_bin.reshape(len(test1_bin), -1)
            test2_bin = test2_bin.reshape(len(test2_bin), -1)

            # Get best fit coefficients, test_fit ,from least-square fit of references,
            # ref_bin, to test, test_bin. (And same for another test signal _Y)
            test1_fit, _, _, _ = lstsq(ref_bin, test1_bin)
            test2_fit, _, _, _ = lstsq(ref_bin, test2_bin)

            # add some warning for rank being less than the channels.
            # lstsq returns array size zero when channels are linear combination of each other.
            # so we calculate residuals manually here

            # calculating residuals
            test1_res = test1_bin - np.matmul(ref_bin, test1_fit)
            test2_res = test2_bin - np.matmul(ref_bin, test2_fit)
            # multiplying residuals = forming the CSD
            # flattening because array is still technically 2D, with dimensions 1 x number_averages
            self.CSD[left_edge:right_edge] = np.ndarray.flatten(
                test1_res * test2_res.conj()
            )
            if self.ap.is_onesided:
                # in one-sided case, scale factor 2x should be applied to properly normalize CSD
                self.CSD[left_edge:right_edge] *= 2.0
            left_edge = right_edge

    def average_CSD(self):
        """Construct CSD and average using Daniell averaging method (`daniell_average`)"""
        # do correct scaling for density or spectrum
        if self.ap.scaling == "density":
            self.CSD /= self.ap.sample_rate * (self.ap.win * self.ap.win).sum()
        else:  # can only be "spectrum" - this argument already sanitized by Daniell method
            self.CSD /= self.ap.win.sum() ** 2
        # and override scale argument for Daniell method to prevent double scaling
        self.ap.scale = 1.0
        # also override bias_correction (different because we have multiple reference channels)
        self.ap.set_bias_correction(
            self.ap.bias_correction(self.CSD)
            - len(self.reference_fft) / np.array(self.bin_widths)
        )

        # remove imaginary part if it's zero
        if not np.iscomplex(self.CSD).any():
            self.CSD = np.real(self.CSD)

        # propagate parameters from time series
        timeseries = self.test1
        if self.test1.name is not None and self.test2.name is not None:
            timeseries.name = (
                "Coherent subtraction from CSD("
                + self.test1.name
                + ","
                + self.test2.name
                + ")"
            )
        elif self.test1 == self.test2 and self.test1.name is not None:
            timeseries.name = "Coherent subtraction from PSD(" + self.test1.name + ")"
        else:
            timeseries.name = "Coherent subtraction from PSD"
        # and average
        return daniell_average(self.frq, self.CSD, timeseries, self.ap)
