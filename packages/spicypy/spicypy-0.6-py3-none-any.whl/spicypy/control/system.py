"""
Class extending functionality of StateSpace from python control

| Artem Basalaev <artem[dot]basalaev[at]physik.uni-hamburg.de>
| Christian Darsow-Fromm <cdarsowf[at]physnet.uni-hamburg.de>
"""
import copy

import control
import numpy as np
from spicypy.signal.time_series import TimeSeries
from spicypy.control.connection import Connection


class System(control.LinearICSystem):
    """
    Class to model control systems and their response

    """

    def __init__(self, sys, name=None):
        """Constructor takes either control.LinearICSystem, control.InputOutputSystem, control.StateSpace, control.TransferFunction object, which is then converted to control.InterconnectedSystem, which is held by this System class.

        Parameters
        ----------
        sys : System, control.LinearICSystem, control.InputOutputSystem, control.StateSpace, control.TransferFunction
            input control system
        """

        # be careful to preserve desired name through conversions
        if name is None:
            name = sys.name

        if isinstance(sys, System):
            # already have spicypy.System, just assign it to self
            self.__dict__ = copy.deepcopy(sys.__dict__)
            self.name = name
            return

        if isinstance(sys, control.LinearICSystem):
            # have instance of parent class, assign everything to self
            self.__dict__ = copy.deepcopy(sys.__dict__)
            self.name = name
            self.connection = None
            return

        # try to convert system to LinearICSystem, in several stages
        sys_orig = (
            sys  # keep original system to show in error at the end if conversion failed
        )

        # first deal with TransferFunction, convert to StateSpace
        if isinstance(sys, control.TransferFunction):
            sys = control.tf2ss(sys)
            sys.name = name

        # then deal with StateSpace, convert to InputOutputSystem
        ss_sys = None  # save StateSpace if we got one, helps construct LinearICSystem properly
        if isinstance(sys, control.StateSpace):
            ss_sys = sys
            sys = control.ss2io(sys)
            sys.name = name

        # finally, with InputOutputSystem, convert to LinearICSystem
        if isinstance(sys, control.InputOutputSystem):
            inplist = list(sys.input_index.keys())
            for i in range(len(inplist)):
                inplist[i] = sys.name + "." + inplist[i]
            outlist = list(sys.output_index.keys())
            for i in range(len(outlist)):
                outlist[i] = sys.name + "." + outlist[i]
            ic_sys = control.InterconnectedSystem(
                [sys], inplist=inplist, outlist=outlist
            )
            super().__init__(ic_sys, ss_sys=ss_sys)
            self.name = name
            self.connection = None
            return

        # if reached here, that means all possibilities of conversion exhausted, throw an error
        raise ValueError(
            "Could not convert object", sys_orig, "into control.LinearICSystem"
        )

    def feedback(self, other=1, sign=-1, params=None):
        """Add a feedback connection.

        Parameters
        ----------
        other : control.StateSpace
            Another system (controller)
        params : dict, optional
            Parameter values for the systems.  Passed to the evaluation functions for the system as default values, overriding internal defaults.
        sign : int
            Sign determining whether it's a negative or a positive feedback

        Returns
        -------
        System :  System
            Control system with feedback connection
        """

        sys_feedback = System(super().feedback(other, sign, params))
        if sign == -1:
            type = "negative feedback"
        elif sign == 1:
            type = "positive feedback"
        else:
            raise ValueError(
                "Sign for feedback can only be -1 (negative feedback) or 1 (positive feedback)"
            )

        sys_feedback.connection = Connection(self, other, type=type)

        return sys_feedback

    def response(self, time_series, *args, **kwargs):
        """Calculate system's response to an input signal.

        Parameters
        ----------
        time_series : TimeSeries, list of TimeSeries
            input signal time series (or list for MIMO systems)

        Returns
        -------
        time_series : TimeSeries, list of TimeSeries
            output signal time series (or list for MIMO systems)
        """
        if isinstance(time_series, TimeSeries):
            t = np.array(time_series.times)
            v = np.array(time_series.value)
            resp = control.input_output_response(self, t, v, *args, **kwargs)
            return TimeSeries(resp.outputs, times=resp.time)

        if not isinstance(time_series, list):
            raise ValueError(
                "Only TimeSeries or list of TimeSeries is allowed as input signal"
            )
        if len(time_series) != self.ninputs:
            raise ValueError(
                "Length of the input list does not match number of inputs! "
                "For a MIMO system, a signal must be assigned to each input, as a list of TimeSeries. "
                "For no/empty inputs, you can specify `None` as some elements of this list."
            )

        # check that there's non-None time series on input
        ref_ts = None
        for ts in time_series:
            if ts is not None and isinstance(ts, TimeSeries):
                ref_ts = ts
        if ref_ts is None:
            raise ValueError(
                "At least one input must be TimeSeries (others can be None for no/empty input)"
            )

        t = np.array(ref_ts.times)
        v = []
        for ts in time_series:
            if ts is None:
                ts = TimeSeries(np.zeros(len(ref_ts.times)))
                ts.times = ref_ts.times
            elif not (np.array(ts.times) == t).all():
                raise ValueError("All TimeSeries must be aligned in time")
            v.append(np.array(ts.value))
        v = np.array(v)

        resp = control.input_output_response(self, t, v, *args, **kwargs)
        ts_list = []
        for output in resp.outputs:
            ts_list.append(TimeSeries(output, times=resp.time))
        return ts_list

    def add_controller(
        self, control_sys, feedin, feedout, control_names=None, negative_feedback=True
    ):  # pylint: disable=too-many-branches
        """Lets you build a Matlab-like MIMO feedback system based on control.interconnect funtion.

        Parameters
        ----------
        control_sys :   list of control.TransferFunction
            List of filters in Transfer-Function form
        feedin      :   list
            List of inputs to be connected
        feedout     :   list
            List of outputs to be connected
        control_names   :   list of str
            List of names for the control.TransferFunction in control_sys (optional, default = None)
        negative_feedback   :   bool
            Select if you want negative feedback or not (optional, default = True)

        Returns
        -------
        sys_interc  :   control.LinearICSystem
            Interconnected System
        """

        # Check if control_sys is a list of TransferFunctions
        for index, filter in enumerate(control_sys):
            if isinstance(filter, control.TransferFunction) is True:
                pass
            else:
                raise ValueError(
                    "filter", index, "is not in control.TransferFunction form"
                )

        # Check if filters are proper
        for index, filter in enumerate(control_sys):
            if len(filter.num[0][0]) > len(filter.den[0][0]):
                raise ValueError(
                    "TransferFunction",
                    index,
                    "is improper: Order of denominator has to be larger or equal to order of numerator",
                )

        # Check for control_names and adapt standard naming scheme
        if control_names is None:
            control_names = [filter.name for filter in control_sys]

        if len(control_names) != len(control_sys):
            raise ValueError(
                "control_names has to be either None or a list of the same length as control_sys"
            )

        # Check if feedin and feedout have the same dimensions as control_sys
        if len(feedin) != len(feedout) != len(control_sys):
            raise ValueError(
                "feedin, feedout and control_sys need to be the same length"
            )

        # Check sign of feedback
        if isinstance(negative_feedback, bool) is False:
            raise ValueError("negative_feedback has to be either True or False")
        feedback = ""
        if negative_feedback is True:
            feedback = "-"

        # Convert filters to LinearIOSystem and give name
        control_sys = self._controller_tf_to_io(control_sys, control_names)

        # Prepare connection matrix
        connections = []
        # Create connections
        for i, index_in, index_out in zip(
            np.arange(0, len(feedin) + 1), feedin, feedout
        ):
            connections.append(
                [
                    control_sys[i].name + ".u[0]",
                    self.name + ".y[" + str(index_in) + "]",
                ]
            )
            connections.append(
                [
                    self.name + ".u[" + str(index_out) + "]",
                    feedback + control_sys[i].name + ".y[0]",
                ]
            )

        # create sadly necessary helper bs (until control version 0.10)
        inp = []
        outp = []

        ninputs = self.ninputs
        noutputs = self.noutputs

        for i in range(ninputs):
            inp.append(self.name + ".u[" + str(i) + "]")
        for i in range(noutputs):
            outp.append(self.name + ".y[" + str(i) + "]")

        # compute interconnected system
        sys_interc = control.interconnect(
            [self, *control_sys], connections=connections, inplist=inp, outlist=outp
        )
        return System(sys_interc)

    def _controller_tf_to_io(self, control_sys, control_names):
        """Helper method to convert control.TransferFunction object into control.LinearIOSystem

        Parameters
        ----------
        control_sys :   list of control.TransferFunction
            list of control.Transferfunction to be converted into control.LinearIOSystem
        control_names   :   list of str
            list of names to be given to the control filters

        Returns
        -------
        control_sys :  list of control.LinearIOSystem
            Same as input parameter but now as list of control.LinearIOSystem
        """

        for index, filter in enumerate(control_sys):
            control_sys[index] = control.tf2io(filter, name=control_names[index])
        return control_sys

    def __mul__(self, sys):
        """Add a sequential connection

        Parameters
        ----------
        sys : control.StateSpace, control.TransferFunction
            input control system

        Returns
        -------
        System :  System
            Control system with sequential connection
        """
        sys_sequential = System(super().__mul__(sys))
        sys_sequential.connection = Connection(self, sys, type="sequential")

        return sys_sequential

    def __add__(self, sys):
        """Add a parallel connection

        Parameters
        ----------
        sys : control.StateSpace, control.TransferFunction
            input control system

        Returns
        -------
        System :  System
            Control system with parallel connection
        """
        sys_parallel = System(super().__add__(sys))
        sys_parallel.connection = Connection(self, sys, type="parallel")

        return sys_parallel
