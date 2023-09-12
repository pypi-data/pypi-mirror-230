"""
============
Daniell averaging method for CSD
============

| Modified for Spicypy by Artem Basalaev <artem[dot]basalaev[at]physik.uni-hamburg.de>
| Reviewed by Christian Darsow-Fromm <cdarsowf[at]physnet.uni-hamburg.de>

Original description:

An upgrade to Pooya Saffarieh's, and Sam Scherf's asd2 port to Python.
This attemts to adress the following main issue, make 'csd_daniell' look like
'scipy.signal.csd' - with the goal of adding 'csd_daniell' to the
'scipy.signal' toolbox. This should offload the code maintanence to a
community with sufficient time and skill to do this.

Addresses:
    - Kwarg pass through
    - Axes
    - CSD vs ASD, CSD is ALWAYS more versatile
    - Harmonising with Scipy Library

Sources:
    - https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.csd.html
    - https://github.com/scipy/scipy/blob/v1.8.0/scipy/signal/_spectral_py.py #L454-L603
    - https://github.com/scipy/scipy/blob/v1.8.0/scipy/signal/_spectral_py.py #L1579-L1869
    - https://gitlab.nikhef.nl/6d/6dscripts/-/blob/master/SpectralAnalyzer/asd2.py
    - https://git.ligo.org/sam.scherf/ftools/-/blob/master/ftools/daniell.py
    - https://git.ligo.org/sam.scherf/ftools/-/blob/master/ftools/_utils.py

| Authors: Nathan A. Holland, Pooya Saffarieh, Abhinav Petra, Conor Mow-Lowry
| Associated Authors: Sam Scherf
| Contact: nholland@nikhef.nl
| Date: 2022-04-12
"""
from warnings import warn

import numpy as np
from gwpy.signal.spectral._utils import scale_timeseries_unit
from scipy.fft import fftshift, ifftshift  # pylint: disable=no-name-in-module
from scipy.signal import csd
from scipy.signal import get_window

from spicypy.signal.frequency_series import FrequencySeries


def daniell(*args, **kwargs):  # pylint: disable=too-many-branches
    """Calculate the CSD of a `TimeSeries` using Daniell's method.
    Frequency domain averaging of the CSD.

    Parameters
    ----------
    args : `list`
        timeseries: `TimeSeries`
            input time series (if only one specified, calculates PSD)
        other: `TimeSeries`, optional
            second input time series
        nfft: `int`
            number of samples per FFT, only value equal to full time series length is accepted
    kwargs : `dict`
        overlap : `float`, optional
            number of seconds of overlap between FFTs. User-specified value ignored, algorithm uses no overlap.
        fftlength : `float`, optional
            number of seconds in single FFT. User-specified value ignored, algorithm uses full duration.
        window : `str`, `numpy.ndarray`, optional
            Window function to apply to timeseries prior to FFT. See :func:`scipy.signal.get_window` for details on acceptable formats. Defaults to 'hann'.
        number_averages: `int`, optional
            Window size for averaging (number of bins) in frequency domain. Must be an odd number. If "binning" is specified to be "logarithmic", window size will depend on bin number as `number_averages + floor(log_base ** bin_number)`
        binning: `str`, optional
            Either "constant" for constant averaging window size = `number_averages` (default) or "logarithmic" for window size depending on bin number as `number_averages + floor(log_base ** bin_number)`
        log_base: `float`, optional
            Log base for logarithmic averaging window size. Default 1.05.
        average: `str`, optional
            Averaging function to use, either "mean" (default) or "median".
        scaling: `str`, optional
            Scaling of the CSD, either "density" (default) or "spectrum".
        additional arguments, passed to scipy.signal.CSD

    Returns
    -------
    fs: FrequencySeries
        resulting CSD
    """

    try:
        timeseries, nfft = args
        other = timeseries
    except ValueError:
        timeseries, other, nfft = args

    # Convert the inputs to numpy arrays.
    x = np.asarray(timeseries.value)
    y = np.asarray(other.value)

    if len(x) != len(y):
        raise ValueError("Time series must have the same length (number of samples)!")

    # No nfft for Daniell method.
    if nfft != len(x):
        raise ValueError(
            "nfft argument is not supported by Daniell averaging method; "
            "single FFT covering the full duration is calculated, with averaging performed in frequency domain."
        )

    # extract the rest of parameters
    sample_rate = timeseries.sample_rate.decompose().value
    ap = AveragingParameters(sample_rate, len(x), **kwargs)

    # Take the CSD.
    # Averaging isn't done by 'csd'.
    # In general the frequency vector has the ordering:
    #  0, f_positive, f_negative
    # and set noverlap to 0 (no overlap with Daniell method)
    noverlap = 0
    nperseg = len(x)  # full length of time series used for the (only) segment
    frq, CSD = csd(
        x,
        y,
        fs=sample_rate,
        window=ap.window,
        nperseg=nperseg,
        noverlap=noverlap,
        nfft=ap.nfft,
        **ap.kwargs,
    )
    # scipy returns complex values with zero imaginary part... cast it to real
    if not np.iscomplex(CSD).any():
        CSD = np.real(CSD)

    # Perform Daniell's averaging.
    frq, CSD, ap = daniell_rearrange_fft(frq, CSD, ap)
    return daniell_average(frq, CSD, timeseries, ap)


def daniell_average(frq, CSD, timeseries, ap):
    """Frequency domain averaging of the CSD.

    Parameters
    ----------
    frq : `np.array` of `float`
        frequency array
    CSD : `np.array` of `float`
        powers array
    timeseries: `TimeSeries`
        one (any of the two) of the original time series from which CSD was calculated. Needed to extract optional information such as channel name etc.
    ap: `AveragingParameters`
        parameters for averaging

    Returns
    -------
    fs: FrequencySeries
        resulting CSD
    """
    # start with CSD itself (potentially need to treat complex numbers)
    if np.iscomplexobj(CSD):
        CSD_averaged = _average(CSD.real, ap) + 1j * _average(CSD.imag, ap)
    else:  # Easy for real valued.
        CSD_averaged = _average(CSD, ap)

    # follow up with the rest: averaging frequency array and rearranging the fft order back, see `daniell_rearrange_fft`
    frq_ap = ap
    frq_ap.avg_func = np.median  # always use np.median for averaging frequency values
    frq_averaged = _average(frq, frq_ap)
    if ap.is_onesided:
        # fix DC bin - frequency equals 0 for it, not average frequency corresponding to DC bin in original CSD
        frq_averaged[0] = 0.0
    else:
        # rearrange fft back
        CSD_averaged = ifftshift(CSD_averaged)
        frq_averaged = ifftshift(frq_averaged)

    # Correct for bias.
    CSD_averaged /= ap.bias_correction(CSD)
    CSD_averaged *= ap.scale

    # generate FrequencySeries and return
    unit = scale_timeseries_unit(timeseries.unit, ap.scaling)
    return FrequencySeries(
        CSD_averaged,
        unit=unit,
        frequencies=frq_averaged,
        name=timeseries.name,
        epoch=timeseries.epoch,
        channel=timeseries.channel,
    )


def _average(CSD, ap):
    """Average CSD, helper function that is called multiple times

    Parameters
    ----------
    CSD : `np.array` of `float`
        input CSD
    ap: `AveragingParameters`
        parameters for averaging

    Returns
    -------
    CSD: `np.array` of `float`
        resulting CSD
    """
    left_edge = 0
    edges, _ = ap.window_edges(CSD)
    for right_edge in edges:
        averaged_value = ap.avg_func(CSD[left_edge:right_edge])
        if left_edge == 0:  # first bin, create CSD
            CSD_averaged = np.array(averaged_value)
        else:
            CSD_averaged = np.append(CSD_averaged, averaged_value)
        left_edge = right_edge
    return CSD_averaged


def daniell_rearrange_fft(frq, CSD, ap):
    """Rearrange FFT/CSD according to daniell method

    Parameters
    ----------
    frq : `np.array` of `float`
        frequency array
    CSD : `np.array` of `float`
        input CSD
    ap: `AveragingParameters`
        parameters for averaging

    Returns
    -------
    frq : `np.array` of `float`
        modified frequency array
    CSD : `np.array` of `float`
        modified CSD
    ap: `AveragingParameters`
        modified parameters for averaging (DC_edge, is_onesided calculated here)
    """
    ap.is_onesided = not np.any(np.less(frq, 0))
    if ap.is_onesided:
        start_drop = ap.number_averages // 2 + 1
        ap.DC_edge = start_drop
        end_drop = -1 * (frq[start_drop:].size % ap.number_averages)
        if end_drop == 0:
            end_drop = None

        frq = frq[:end_drop]
        CSD = CSD[:end_drop]
    else:
        # rearrange: put zero frequency in the middle of spectrum, between negative and positive frequencies
        frq = fftshift(frq)
        CSD = fftshift(CSD)

        # Deal with even case.
        if (frq.size % 2) == 0:
            # Cut off the lowest frequency point, which has no
            # symmetric, positive counterpart.
            frq = frq[1:]
            CSD = CSD[1:]

        total_to_drop = frq.size % ap.number_averages

        end_drop = -1 * (total_to_drop // 2)
        if end_drop == 0:
            end_drop = None

        start_drop = total_to_drop // 2
        if (total_to_drop % 2) != 0:
            # Need to drop the lowest frequency point too.
            start_drop += 1

        frq = frq[start_drop:end_drop]
        CSD = CSD[start_drop:end_drop]

    return frq, CSD, ap


class AveragingParameters:  # pylint: disable=too-many-instance-attributes
    """
    Class holding averaging parameters
    """

    def __init__(
        self, sample_rate, n_samples, **kwargs
    ):  # pylint: disable=too-many-branches
        """Constructor takes sample rate, number of samples and other optional arguments

        Parameters
        ----------
        sample_rate : int
            sampling rate of input time series
        n_samples : int
            length of time series (number of samples)
        kwargs : `dict`
            overlap : `float`, optional
                number of seconds of overlap between FFTs. User-specified value ignored, algorithm uses no overlap.
            fftlength : `float`, optional
                number of seconds in single FFT. User-specified value ignored, algorithm uses full duration.
            window : `str`, `numpy.ndarray`, optional
                Window function to apply to timeseries prior to FFT. See :func:`scipy.signal.get_window` for details on acceptable formats. Defaults to 'hann'.
            number_averages: `int`, optional
                Window size for averaging (number of bins) in frequency domain. Must be an odd number. If "binning" is specified to be "logarithmic", window size will depend on bin number as `number_averages + floor(log_base ** bin_number)`
            binning: `str`, optional
                Either "constant" for constant averaging window size = `number_averages` (default) or "logarithmic" for window size depending on bin number as `number_averages + floor(log_base ** bin_number)`
            log_base: `float`, optional
                Log base for logarithmic averaging window size. Default 1.05.
            average: `str`, optional
                Averaging function to use, either "mean" (default) or "median".
            scaling: `str`, optional
                Scaling of the CSD, either "density" (default) or "spectrum".
            additional arguments, passed to scipy.signal.CSD
        """
        # No overlap for Daniell method.
        overlap = kwargs.pop("overlap", 0)
        if overlap is not None and overlap != 0:
            raise ValueError(
                "overlap argument is not supported by Daniell averaging method; "
                "single FFT covering the full duration is calculated, with averaging performed in frequency domain."
            )
        # noverlap is specified by GWpy by default, get rid of it
        if "noverlap" in kwargs:
            kwargs.pop("noverlap")

        # No fftlength for Daniell method.
        if kwargs.get("fftlength"):
            raise ValueError(
                "fftlength argument is not supported by Daniell averaging method; "
                "single FFT covering the full duration is calculated, with averaging performed in frequency domain."
            )
        nfft = int(n_samples + kwargs.pop("pad_length", 0))

        # get window function
        window = kwargs.pop("window_", None)
        window = "hann" if window is None else window
        # clean up default value from kwargs
        if "window" in kwargs:
            kwargs.pop("window")
        if not isinstance(window, str):
            warn(
                "Specifying window as an array for Daniell averaging method is not supported, defaulting to 'hann' window"
            )
            window = "hann"
        win = get_window(window, n_samples)

        # For now REQUIRES an odd number of averages, to handle complex
        # data types.
        number_averages = kwargs.pop("number_averages", 9)
        if (number_averages % 2) == 0:
            err = (
                f"Only an odd number of averages, not {number_averages} are "
                + "implemented - for complex symmetry reasons."
            )
            raise NotImplementedError(err)

        if int(number_averages) != number_averages or number_averages < 1:
            err = f"Number of averages must be an odd integer greater or equal 1 (currently set to {number_averages})"
            raise ValueError(err)

        binning = kwargs.pop("binning", "constant")
        if binning == "constant" and "log_base" in kwargs:
            warn(
                "`log_base` is specified but binning is set to 'constant'. "
                "Specified `log_base` value will be ignored!"
            )
        log_base = float(kwargs.pop("log_base", 1.05))

        # Check the averaging method.
        average = kwargs.pop("average", "mean")
        if average == "mean":
            avg_func = np.mean
        elif average == "median":
            avg_func = np.median
        else:
            err = (
                "Available options for <average> are 'mean' and 'median'"
                + f" not {average}."
            )
            raise ValueError(err)

        # scale as spectral density or spectrum
        scaling = kwargs.pop("scaling", "density")
        if scaling == "density":
            scale = 1.0  # scipy.signal.csd already scales for density
        elif scaling == "spectrum":
            scale = (sample_rate * (win * win).sum()) / win.sum() ** 2
        else:
            err = (
                f'Unknown scaling: {scaling}, only "density" and'
                + ' "spectrum" are supported.'
            )
            raise ValueError(err)

        # set attributes from arguments above
        self.average = average
        self.window = window
        self.win = win
        self.scale = scale
        self.scaling = scaling
        self.sample_rate = sample_rate
        self.number_averages = number_averages
        self.binning = binning
        self.log_base = log_base
        self.avg_func = avg_func
        self.nfft = nfft
        self.kwargs = kwargs

        # set defaults for other attributes
        self.DC_edge = 0
        self._bias_correction = None
        self.is_onesided = True

    def window_edges(self, CSD):
        """Calculate window edges (array indices) for each averaging bin

        Parameters
        ----------
        CSD : `np.array` of `float`
            input CSD

        Returns
        -------
        edges : `list` of `int`
            window edges (array indices) for each averaging bin
        bin_widths : `list` of `int`
            size (width) of each averaging bin
        """
        p = 0
        startpoint = 0
        endpoint = 0
        edges = []
        bin_widths = []
        if self.DC_edge != 0:  # we have a DC bin
            edges.append(self.DC_edge)
            startpoint += self.DC_edge
            bin_widths.append(self.DC_edge)

        if startpoint + self.number_averages > CSD.size:
            raise ValueError(
                "Cannot do averaging because CSD contains less elements than number_averages (+ DC bin). "
                "Try to reduce number_averages parameter to a smaller value."
            )

        while endpoint < CSD.size:
            # get right edge of current window
            step = int(self.number_averages + np.floor(self.log_base**p - 1.0))
            endpoint = startpoint + step
            edges.append(endpoint)
            bin_widths.append(endpoint - startpoint)
            startpoint += step
            if (
                self.binning == "logarithmic"
            ):  # in log case, each next window is number_averages + log_base ** p
                p = p + 1
        # fix last window edge to be as many elements as we actually have left
        if edges[-1] != CSD.size:
            edges[-1] = CSD.size
        return edges, bin_widths

    def bias_correction(self, CSD):
        """Calculate correction for median bias for each bin (depends on bin width)

        Parameters
        ----------
        CSD : `np.array` of `float`
            input CSD

        Returns
        -------
        bias_correction : `list` of `float` or `float`
            either list of float for different correction in each bin, or a single float for same correction in every bin.
        """
        if self._bias_correction is not None:
            # bias correction is already calculated, or perhaps set externally
            return self._bias_correction
        bias_correction = 1.0
        if self.average == "median":
            _, bin_widths = self.window_edges(CSD)
            bias_correction = []
            for width in bin_widths:
                if width == 1:  # no averaging in this case, hence no bias
                    correction = 1.0
                else:
                    # bias correction from _median_bias in Scipy 1.8
                    ii_2 = 2 * np.arange(1.0, (width - 1) // 2 + 1)
                    correction = 1 + np.sum(1.0 / (ii_2 + 1) - 1.0 / ii_2)
                bias_correction.append(correction)
            bias_correction = np.array(bias_correction)
        return bias_correction

    def set_bias_correction(self, correction):
        """Manually set bias correction

        Parameters
        ----------
        correction : `list` of `float` or `float`
            either list of float for different correction in each bin, or a single float for same correction in every bin.
        """
        self._bias_correction = correction
