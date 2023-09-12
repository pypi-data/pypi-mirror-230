"""
Class calculating transfer function between two time series (result is FrequencySeries).

Authors:
    | Artem Basalaev <artem[dot]basalaev[at]physik.uni-hamburg.de>
    | Christian Darsow-Fromm <cdarsowf[at]physnet.uni-hamburg.de>
    | Abhinav Patra <patraa1[at]cardiff.ac.uk>
    | Octavio Vega <ovega84[at]mit.edu>
"""
from typing import Optional

import gwpy
import numpy as np
import matplotlib

from spicypy.signal.frequency_series import FrequencySeries
from spicypy.signal.time_series import TimeSeries


class TransferFunction:  # pylint: disable=too-many-instance-attributes
    """
    Class calculating transfer function between two time series (result is FrequencySeries)

    """

    def __init__(
        self,
        ts1: Optional[TimeSeries] = None,
        ts2: Optional[TimeSeries] = None,
        tf: Optional[FrequencySeries] = None,
        name="Generic transfer function",
        **kwargs,
    ):
        """Constructor takes either two time series _or_ another TransferFunction object

        Parameters
        ----------
        ts1 : `TimeSeries`
            first `TimeSeries`
        ts2 : `TimeSeries`
            second `TimeSeries`
        tf : `TransferFunction`
            alternative constructor with another TransferFunction object
        name : `str`, optional
            name, if not provided constructed from input time series names
        kwargs : `dict`, optional
            any additional arguments that `TimeSeries.psd()` or `TimeSeries.csd()` can take, e.g. averaging method
        """
        self._ts1 = ts1
        self._ts2 = ts2
        self._kwargs = kwargs
        self._coherence = None
        self._psd1 = None
        self._psd2 = None
        self._csd = None
        self._tf = tf
        self._name = name

        # if we specify the transfer function directly (nothing to calculate)
        if self._tf is not None:
            # check that other args are not specified
            if ts1 is not None or ts2 is not None:
                raise ValueError(
                    "Transfer function was specified on input together with time series"
                )
            self._tf.name = name
            return

        if ts1 is None or ts2 is None:
            raise ValueError("Two time series should be specified on input (got <2)")

    @property
    def ts1(self):
        """Property holding first time series

        Returns
        -------
        psd1 :  TimeSeries
            first time series
        """
        return self._ts1

    @property
    def ts2(self):
        """Property holding second time series

        Returns
        -------
        psd1 :  TimeSeries
            second time series
        """
        return self._ts2

    @property
    def psd1(self):
        """Calculate the PSD of the first time series

        Returns
        -------
        psd1 :  FrequencySeries
            a data series containing the PSD.
        """
        if self._psd1 is None:
            self._psd1 = self._ts1.psd(**self._kwargs)
        return self._psd1

    @property
    def psd2(self):
        """Calculate the PSD of the second time series

        Returns
        -------
        psd2 :  FrequencySeries
            a data series containing the PSD.
        """
        if self._psd2 is None:
            self._psd2 = self._ts2.psd(**self._kwargs)
        return self._psd2

    @property
    def csd(self):
        """Calculate the CSD of the first time series to the second

        Returns
        -------
        psd1 :  FrequencySeries
            a data series containing the CDD.
        """
        if self._csd is None:
            self._csd = self._ts1.csd(self._ts2, **self._kwargs)
        return self._csd

    @property
    def tf(self):
        """Calculate the transfer function

        Returns
        -------
        tf :  FrequencySeries
            a data series containing the transfer function.
        """
        if self._tf is None:
            self._tf = self.csd / self.psd1
            # if we didn't already specify a nice name for it...
            if self._name == "Generic transfer function":
                self.tf.name = (
                    f"Transfer Function between {self._ts1.name} and {self._ts2.name}"
                )
        return self._tf

    @property
    def coherence(self):
        """Calculate coherence between input time series

        Returns
        -------
        coherence :  FrequencySeries
            a data series containing normalized coherence in frequency domain
        """
        if self._coherence is None:
            self._coherence = self._ts1.coherence(self._ts2, **self._kwargs)
        return self._coherence

    def plot(self, coherence=False, **kwargs) -> matplotlib.figure.Figure:
        """Plot transfer function (magnitude and phase) and optionally coherence

        Returns
        -------
        plot :  :class:`matplotlib.figure.Figure`
            a matplotlib plot that can be further modified by the user
        """
        if self.tf is None:
            raise AttributeError(
                "Somehow missing transfer function, this should never happen"
            )
        if self._ts1 is None or self._ts2 is None:
            return self.tf.plot(**kwargs)

        traces = [np.abs(self.tf), np.angle(self.tf, deg=True)]
        if coherence:
            traces.append(self.coherence)

        # log axis by default
        xscale = kwargs.pop("xscale", None)
        if xscale is None:
            xscale = "log"
        yscale = kwargs.pop("yscale", None)
        if yscale is None:
            yscale = "log"

        plot = gwpy.plot.Plot(
            *traces,
            separate=True,
            figsize=(10, 10),
            xscale=xscale,
            yscale=yscale,
            **kwargs,
        )
        plot.align_labels()

        # Magnitude of transfer function
        plot.axes[0].set_title(self.tf.name)
        if self._ts1.unit == self._ts2.unit:
            plot.axes[0].set_ylabel("Magnitude")
        else:
            plot.axes[0].set_ylabel(self._ts2.unit / self._ts1.unit)
        # Phase of transfer function
        plot.axes[1].set_ylabel("Phase [deg]")
        plot.axes[1].set_yscale("linear")

        if coherence:
            # Coherence between input time series
            plot.axes[2].set_title(traces[2].name)
            plot.axes[2].set_ylabel("Coherence")
            plot.axes[2].set_yscale("linear")

            if np.all(np.isclose(traces[2].value, 1.0, rtol=0.99)):
                plot.axes[2].set_ylim(0.7, 1.3)

        plot.tight_layout()

        return plot
