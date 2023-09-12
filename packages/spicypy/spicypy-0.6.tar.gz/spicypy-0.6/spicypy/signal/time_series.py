"""
Class extending functionality of :obj:`gwpy.timeseries.timeseries.TimeSeries` from GWpy.

Authors:
    | Artem Basalaev <artem[dot]basalaev[at]physik.uni-hamburg.de>
    | Christian Darsow-Fromm <cdarsowf[at]physnet.uni-hamburg.de>
    | Abhinav Patra <patraa1[at]cardiff.ac.uk>
    | Octavio Vega <ovega84[at]mit.edu>
"""
from warnings import warn
import numpy as np
import gwpy.timeseries
from gwpy.signal import spectral

from spicypy.signal.spectral import daniell, lpsd
from spicypy.signal.coherent_subtraction import coherent_subtraction

spectral.register_method(daniell)
spectral.register_method(lpsd)


class TimeSeries(gwpy.timeseries.TimeSeries):
    """
    Class to model signals (time series)

    """

    def asd(self, fftlength=None, overlap=None, window=None, **kwargs):
        """Calculate the ASD `FrequencySeries` of this `TimeSeries`

        Parameters
        ----------
        fftlength : `float`, optional
            number of seconds in single FFT. Default behavior:

            * For Daniell averaging method (`method='daniell'`): user-specified value ignored, calculates single FFT covering full duration and then performs averaging in frequency domain.
            * For LPSD averaging method (`method='lpsd'`): user-specified value ignored, algorithm calculates optimal segment lengths.
            * For other averaging methods: defaults to a single FFT covering the full duration

        overlap : `float`, optional
            number of seconds of overlap between FFTs. Default behavior:

            * For Daniell averaging method (`method='daniell'`): user-specified value ignored, no overlap possible because a single FFT is calculated.
            * For other averaging methods: defaults to the recommended overlap for the given window (if given), or 0

        window : `str`, `numpy.ndarray`, optional
            Window function to apply to timeseries prior to FFT. Behavior depends on averaging method:

            * For LPSD averaging method (`method='lpsd'`): only `str` type is allowed. Possible values: 'hann', 'hanning', 'ham', 'hamming', 'bartlett', 'blackman', 'kaiser'. Defaults to 'kaiser'.
            * For other averaging methods: see :func:`scipy.signal.get_window` for details on acceptable formats. Defaults to 'hann'.

        **kwargs
            method : `str`, optional
                FFT-averaging method (default: ``'median'``). The accepted ``method`` arguments are:

                - ``'bartlett'`` : a mean average of non-overlapping periodograms
                - ``'median'`` : a median average of overlapping periodograms
                - ``'welch'`` : a mean average of overlapping periodograms
                - ``'lpsd'`` :  average of overlapping periodograms binned logarithmically in frequency
                - ``'daniell'`` : calculates single fft for the whole time series and averages in frequency domain

            any other keyword arguments accepted by the respective averaging methods. See definitions of corresponding method (`method` keyword). If `method` is not specified, defaults to :class:`gwpy.signal.spectral.csd`

        Returns
        -------
        asd :  FrequencySeries
            a data series containing the ASD
        """

        # work-around to propagate 'window' argument intact for custom averaging methods
        if "method" in kwargs and (
            kwargs["method"] == "daniell" or kwargs["method"] == "lpsd"
        ):
            kwargs["window_"] = window

        return super().asd(fftlength, overlap, window, **kwargs)

    def psd(self, fftlength=None, overlap=None, window=None, **kwargs):
        """Calculate the PSD `FrequencySeries` of this `TimeSeries`

        Parameters
        ----------
        fftlength : `float`, optional
            number of seconds in single FFT. Default behavior:

            * For Daniell averaging method (`method='daniell'`): user-specified value ignored, calculates single FFT covering full duration and then performs averaging in frequency domain.
            * For LPSD averaging method (`method='lpsd'`): user-specified value ignored, algorithm calculates optimal segment lengths.
            * For other averaging methods: defaults to a single FFT covering the full duration

        overlap : `float`, optional
            number of seconds of overlap between FFTs. Default behavior:

            * For Daniell averaging method (`method='daniell'`): user-specified value ignored, no overlap possible because a single FFT is calculated.
            * For other averaging methods: defaults to the recommended overlap for the given window (if given), or 0

        window : `str`, `numpy.ndarray`, optional
            Window function to apply to timeseries prior to FFT. Behavior depends on averaging method:

            * For LPSD averaging method (`method='lpsd'`): only `str` type is allowed. Possible values: 'hann', 'hanning', 'ham', 'hamming', 'bartlett', 'blackman', 'kaiser'. Defaults to 'kaiser'.
            * For other averaging methods: see :func:`scipy.signal.get_window` for details on acceptable formats. Defaults to 'hann'.

        **kwargs
            method : `str`, optional
                FFT-averaging method (default: ``'median'``). The accepted ``method`` arguments are:

                - ``'bartlett'`` : a mean average of non-overlapping periodograms
                - ``'median'`` : a median average of overlapping periodograms
                - ``'welch'`` : a mean average of overlapping periodograms
                - ``'lpsd'`` :  average of overlapping periodograms binned logarithmically in frequency
                - ``'daniell'`` : calculates single fft for the whole time series and averages in frequency domain

            any other keyword arguments accepted by the respective averaging methods.
            See definitions of corresponding method (`method` keyword). If `method` is not specified,
            defaults to gwpy.signal.spectral.csd

        Returns
        -------
        psd :  FrequencySeries
            a data series containing the PSD
        """

        # work-around to propagate 'window' argument intact for custom averaging methods
        if "method" in kwargs and (
            kwargs["method"] == "daniell" or kwargs["method"] == "lpsd"
        ):
            kwargs["window_"] = window
        elif window is None:
            # default to 'hann' for standard GWpy methods
            window = "hann"

        return super().psd(fftlength, overlap, window, **kwargs)

    def csd(self, other, fftlength=None, overlap=None, window=None, **kwargs):
        """Calculate the CSD `FrequencySeries` for two `TimeSeries`

        Parameters
        ----------
        other : `TimeSeries`
            the second `TimeSeries` in this CSD calculation

        fftlength : `float`, optional
            number of seconds in single FFT. Default behavior:

            * For Daniell averaging method (`method='daniell'`): user-specified value ignored, calculates single FFT covering full duration and then performs averaging in frequency domain.
            * For LPSD averaging method (`method='lpsd'`): user-specified value ignored, algorithm calculates optimal segment lengths.
            * For other averaging methods: defaults to a single FFT covering the full duration

        overlap : `float`, optional
            number of seconds of overlap between FFTs. Default behavior:

            * For Daniell averaging method (`method='daniell'`): user-specified value ignored, no overlap possible because a single FFT is calculated.
            * For other averaging methods: defaults to the recommended overlap for the given window (if given), or 0

        window : `str`, `numpy.ndarray`, optional
            Window function to apply to timeseries prior to FFT. Behavior depends on averaging method:

            * For LPSD averaging method (`method='lpsd'`): only `str` type is allowed. Possible values: 'hann', 'hanning', 'ham', 'hamming', 'bartlett', 'blackman', 'kaiser'. Defaults to 'kaiser'.
            * For other averaging methods: see :func:`scipy.signal.get_window` for details on acceptable formats. Defaults to 'hann'.

        **kwargs
            method: `str`, optional
                averaging method for coherence calculation (default: ``'median'``). See above for important difference in arguments. The accepted ``method`` arguments are:

                - ``'bartlett'`` : a mean average of non-overlapping periodograms
                - ``'median'`` : a median average of overlapping periodograms
                - ``'welch'`` : a mean average of overlapping periodograms
                - ``'lpsd'`` :  average of overlapping periodograms binned logarithmically in frequency
                - ``'daniell'`` : calculates single fft for the whole time series and averages in frequency domain

            any other keyword arguments accepted by the respective averaging methods.
            See definitions of corresponding method (`method` keyword).

        Returns
        -------
        csd :  FrequencySeries
            a data series containing the CSD.
        """

        method_func = spectral.csd
        method = kwargs.pop("method", None)
        if method == "daniell":
            method_func = daniell
        elif method == "lpsd":
            method_func = lpsd
        elif method is None:
            # using default GWpy method; in that case, default fftlength will may also be used
            # inform the user of dangers
            if fftlength is None:
                warn(
                    "No 'fftlength' specified, note that in this case single FFT covering whole time series is used"
                )
            if window is None:
                # default to 'hann' for standard GWpy methods
                window = "hann"
        else:
            raise NotImplementedError(
                "Only 'daniell' and 'lpsd' averaging methods are currently implemented in addition to default"
            )

        if method_func is not spectral.csd:
            # work-around to propagate 'window' argument intact for custom averaging methods
            kwargs["window_"] = window

        return spectral.psd(
            (self, other),
            method_func,
            fftlength=fftlength,
            overlap=overlap,
            window=window,
            **kwargs,
        )

    def coherent_subtract(
        self, reference, fftlength=None, overlap=None, window=None, **kwargs
    ):
        """Calculate the frequency-coherence between this `TimeSeries` and another.

        Parameters
        ----------
        reference: list or  `TimeSeriesDict`
            reference time series

        fftlength : `float`, optional
            number of seconds in single FFT. Default behavior:

            * For Daniell averaging method (`method='daniell'`): user-specified value ignored, calculates single FFT covering full duration and then performs averaging in frequency domain.

            (other averaging methods are currently not supported)

        overlap : `float`, optional
            number of seconds of overlap between FFTs. Default behavior:

            * For Daniell averaging method (`method='daniell'`): user-specified value ignored, no overlap possible because a single FFT is calculated.

            (other averaging methods are currently not supported)

        window : `str`, `numpy.ndarray`, optional
            Window function to apply to timeseries prior to FFT.

            see :func:`scipy.signal.get_window` for details on acceptable formats. Defaults to 'hann'.

        **kwargs
            method: `str`, optional
                averaging method for coherence calculation. Currently only 'daniell' is supported

            any other keyword arguments accepted by 'daniell' averaging method

        Returns
        -------
        residual_psd : FrequencySeries
            residual PSD after frequency-domain subtraction of reference time series
        """

        method = kwargs.pop("method", "daniell")
        if method != "daniell":
            raise NotImplementedError(
                "Coherent subtraction is currently implemented only with Daniell averaging "
                "method."
            )
        kwargs["fftlength"] = fftlength
        kwargs["overlap"] = overlap
        kwargs["window_"] = window
        return coherent_subtraction(self, reference, **kwargs)

    def coherence(self, other, fftlength=None, overlap=None, window=None, **kwargs):
        """Calculate the frequency-coherence between this `TimeSeries` and another.

        Parameters
        ----------
        other : `TimeSeries`
            `TimeSeries` signal to calculate coherence with

        fftlength : `float`, optional
            number of seconds in single FFT. Default behavior:

            * For Daniell averaging method (`method='daniell'`): user-specified value ignored, calculates single FFT covering full duration and then performs averaging in frequency domain.
            * For LPSD averaging method (`method='lpsd'`): user-specified value ignored, algorithm calculates optimal segment lengths.
            * For other averaging methods: defaults to a single FFT covering the full duration (**NOTE**: THIS DEFAULT VALUE IN COHERENCE CALCULATION DOES NOT MAKE SENSE FOR MOST REAL APPLICATIONS!)

        overlap : `float`, optional
            number of seconds of overlap between FFTs. Default behavior:

            * For Daniell averaging method (`method='daniell'`): user-specified value ignored, no overlap possible because a single FFT is calculated.
            * For other averaging methods: defaults to the recommended overlap for the given window (if given), or 0

        window : `str`, `numpy.ndarray`, optional
            Window function to apply to timeseries prior to FFT. Behavior depends on averaging method:

            * For LPSD averaging method (`method='lpsd'`): only `str` type is allowed. Possible values: 'hann', 'hanning', 'ham', 'hamming', 'bartlett', 'blackman', 'kaiser'. Defaults to 'kaiser'.
            * For other averaging methods: see :func:`scipy.signal.get_window` for details on acceptable formats. Defaults to 'hann'.

        **kwargs
            method: `str`, optional
                averaging method for coherence calculation. See above for important difference in arguments.
                Defaults to gwpy.signal.spectral.coherence

            any other keyword arguments accepted by the respective averaging methods.
            See definitions of corresponding method (`method` keyword). If `method` is not specified,
            defaults to gwpy.signal.spectral.coherence

        Returns
        -------
        coherence : FrequencySeries
            the coherence `FrequencySeries` of this `TimeSeries` with the other
        """

        method = kwargs.pop("method", None)

        # calculate coherence
        if method == "daniell" or method == "lpsd":
            return self._coherence(
                other,
                fftlength=fftlength,
                overlap=overlap,
                window=window,
                method=method,
                **kwargs,
            )
        elif method is None:
            # using default GWpy method; in that case, default fftlength will may also be used
            # inform the user of dangers
            if fftlength is None:
                warn(
                    "No 'fftlength' specified, note that in this case single FFT covering whole time series is used"
                )
            if window is None:
                # default to 'hann' for standard GWpy methods
                window = "hann"
            return spectral.psd(
                (self, other),
                spectral.coherence,
                fftlength=fftlength,
                overlap=overlap,
                window=window,
                **kwargs,
            )
        else:
            raise NotImplementedError(
                "Only 'daniell' and 'lpsd' averaging methods are currently implemented in addition to default"
            )

    def _coherence(
        self,
        other,
        fftlength=None,
        overlap=None,
        window=None,
        method="daniell",
        **kwargs,
    ):
        """Calculate the frequency-coherence between this `TimeSeries` and another with "custom" averaging methods. This method then calculates coherence using the formula:

        `coherence = np.abs(csd) ** 2 / psd1 / psd2`

        Parameters
        ----------
        other : `TimeSeries`
            `TimeSeries` signal to calculate coherence with

        fftlength : `float`, optional
            number of seconds in single FFT. The only valid value is 'None' since this argument is not supported by "custom" averaging methods.

        overlap : `float`, optional
            number of seconds of overlap between FFTs. Default behavior:

            * For Daniell averaging method (`method='daniell'`): user-specified value ignored, no overlap possible because a single FFT is calculated.
            * For LPSD averaging method: defaults to the recommended overlap for the given window (if given), or 0

        window : `str`, `numpy.ndarray`, optional
            Window function to apply to timeseries prior to FFT. Behavior depends on averaging method:

            * For LPSD averaging method (`method='lpsd'`): only `str` type is allowed. Possible values: 'hann', 'hanning', 'ham', 'hamming', 'bartlett', 'blackman', 'kaiser'. Defaults to 'kaiser'.
            * For other averaging methods: see :func:`scipy.signal.get_window` for details on acceptable formats. Defaults to 'hann'.

        **kwargs
            any other keyword arguments accepted by the respective averaging methods.
            See definitions of corresponding method (`method` keyword).

        Returns
        -------
        coherence : FrequencySeries
            the coherence `FrequencySeries` of this `TimeSeries` with the other
        """

        # work-around to propagate 'window' argument intact for custom averaging methods
        kwargs["window_"] = window

        if method == "daniell":
            method_func = daniell
        elif method == "lpsd":
            method_func = lpsd
        else:
            raise NotImplementedError(
                "Custom coherence calculation is only implemented for 'daniell' and 'lpsd' "
                "averaging methods."
            )
        csd = spectral.psd(
            (self, other),
            method_func=method_func,
            fftlength=fftlength,
            overlap=overlap,
            window=window,
            **kwargs,
        )
        psd1 = spectral.psd(
            self,
            method_func=method_func,
            fftlength=fftlength,
            overlap=overlap,
            window=window,
            **kwargs,
        )
        psd2 = spectral.psd(
            other,
            method_func=method_func,
            fftlength=fftlength,
            overlap=overlap,
            window=window,
            **kwargs,
        )
        coherence = np.abs(csd) ** 2 / psd1 / psd2
        coherence.name = f"Coherence between {self.name} and {other.name}"
        coherence.override_unit("coherence")
        return coherence
