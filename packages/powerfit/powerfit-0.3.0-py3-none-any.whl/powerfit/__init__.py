from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike
from scipy.optimize import curve_fit

from ._version import version  # noqa: F401


class Limit:
    """
    Small helper class to keep track of the lower and upper limits of a data set.

    For example::

        lim = Limit()

        for data in data_set:
            lim += data

        print(lim.lower, lim.upper)
    """

    def __init__(self):
        self._lim = [np.inf, -np.inf]

    @property
    def lower(self):
        return self._lim[0]

    @property
    def upper(self):
        return self._lim[1]

    @property
    def lim(self):
        return np.array(self._lim)

    def update(self, data):
        self._lim = [min([np.min(data), self._lim[0]]), max([np.max(data), self._lim[1]])]

    def __radd__(self, data):
        self.update(data)
        return self

    def __add__(self, data):
        self.update(data)
        return self


def _fit_loglog(
    logx: ArrayLike,
    logy: ArrayLike,
    prefactor: float,
    exponent: float,
    **fit_opts,
) -> (float, float):
    if prefactor is None and exponent is None:

        def f(logx, log_prefactor, exponent):
            return log_prefactor + exponent * logx

        param, pcov = curve_fit(f, logx, logy, **fit_opts)
        prefactor = np.exp(param[0])
        exponent = param[1]
        perr = np.exp(np.sqrt(pcov[0, 0]))
        eerr = np.sqrt(pcov[1, 1])

    elif prefactor is None:

        def f(logx, log_prefactor):
            return log_prefactor + exponent * logx

        param, pcov = curve_fit(f, logx, logy, **fit_opts)
        prefactor = np.exp(param[0])
        perr = np.exp(np.sqrt(pcov[0, 0]))
        eerr = 0

    elif exponent is None:
        log_prefactor = np.log(prefactor)

        def f(logx, exponent):
            return log_prefactor + exponent * logx

        param, pcov = curve_fit(f, logx, logy, **fit_opts)
        exponent = param[0]
        perr = 0
        eerr = np.sqrt(pcov[0, 0])

    return dict(prefactor=prefactor, exponent=exponent, prefactor_error=perr, exponent_error=eerr)


def powerlaw(
    xdata: ArrayLike,
    ydata: ArrayLike,
    yerr: ArrayLike = None,
    yerr_mode: str = "differentials",
    absolute_sigma: bool = True,
    prefactor: float = None,
    exponent: float = None,
    cutoff_upper: int = 0,
    cutoff_lower: int = False,
) -> dict:
    r"""
    Fit a powerlaw :math:`y = c x^b` by a linear fitting of
    :math:`\ln y = \ln c + b \ln x`.

    .. note::

        This function does not support more customised operation like fitting an offset,
        but custom code can be easily written by copy/pasting from here.

    .. warning::

        If this function is used to plot the fit, beware that the fit is plotted using just
        two data-points if the axis is set to log-log scale
        (as the fit will be a straight line on that scale).

    Different modes are available to treat an error estimate (``yerr``) in ``ydata``:

    *   ``"differentials"``: assume that ``yerr << ydata``, such that

        .. math::

            z &\equiv \ln y \\
            \delta z &= \left| \frac{\partial z}{\partial y} \right| \delta y \\
            \delta z &= \frac{\delta y}{y}

    .. seealso::

        `scipy.optimize.curve_fit
        <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html>`__

    :param xdata: Data points along the x-axis.
    :param ydata: Data points along the y-axis.
    :param yerr: Error-bar for ``ydata`` (should be the standard deviation).
    :param yerr_mode: How to treat the error in ``ydata``, see above.
    :param absolute_sigma: Treat (the effective) ``yerr`` as absolute error.
    :param prefactor: Prefactor :math:`c` (fitted if not specified).
    :param exponent: Exponent :math:`b` (fitted if not specified).
    :param cutoff_upper: Automatically remove upper cutoff below (``-1``) or above (``+1``) the fit.
    :param cutoff_lower: Automatically remove lower cutoff below (``-1``) or above (``+1``) the fit.

    :return:
        The fit details as a dictionary::

            prefactor: (Fitted) prefactor.
            exponent: (Fitted) exponent.
            prefactor_error: Estimated error of prefactor.
            exponent_error: Estimated error of exponent.
            pcov: Covariance of fit.
            slice: Slice of the data used for the fit. Warning: negative/NaN entries remove first.
    """
    kwargs = locals()
    xdata = np.array(xdata)
    ydata = np.array(ydata)

    i = np.logical_and(xdata > 0, ydata > 0)
    logx = np.log(xdata[i])
    logy = np.log(ydata[i])

    j = np.logical_or(np.isnan(logx), np.isnan(logy))
    logx = logx[~j]
    logy = logy[~j]

    fit_opts = {}

    if yerr is not None:
        if yerr_mode.lower() == "differentials":
            yerr = np.array(yerr)
            sigma = yerr[i][~j] / ydata[i][~j]
            sigma[yerr[i][~j] == 0] = np.finfo(sigma.dtype).eps  # avoid zero division
            fit_opts["sigma"] = sigma
            fit_opts["absolute_sigma"] = absolute_sigma
        else:
            raise OSError("yerr_mode: did you mean 'differentials'?")

    details = _fit_loglog(logx, logy, prefactor, exponent, **fit_opts)

    cutoff_upper = int(cutoff_upper)
    cutoff_lower = int(cutoff_lower)
    selector = slice(None, None, 1)

    if cutoff_upper:
        while True:
            ly = np.log(details["prefactor"]) + details["exponent"] * logx
            sy = np.sign(logy - ly)[selector].astype(int)
            if not np.all(sy[-2:] == cutoff_upper):
                break
            if selector.stop is None:
                selector = slice(selector.start, -1, 1)
            else:
                selector = slice(selector.start, selector.stop - 1, 1)
            details = _fit_loglog(logx[selector], logy[selector], prefactor, exponent, **fit_opts)

    if cutoff_lower:
        while True:
            ly = np.log(details["prefactor"]) + details["exponent"] * logx
            sy = np.sign(logy - ly)[selector].astype(int)
            if not np.all(sy[:2] == cutoff_lower):
                break
            if selector.start is None:
                selector = slice(1, selector.stop, 1)
            else:
                selector = slice(selector.start + 1, selector.stop, 1)
            details = _fit_loglog(logx[selector], logy[selector], prefactor, exponent, **fit_opts)

    details["slice"] = selector

    return details


def exp(
    xdata: ArrayLike,
    ydata: ArrayLike,
    yerr: ArrayLike = None,
    yerr_mode: str = "differentials",
    absolute_sigma: bool = True,
    prefactor: float = None,
    exponent: float = None,
) -> dict:
    r"""
    Fit an exponential :math:`y = c \exp(b x)` by linear fitting of
    :math`ln y = ln c + b x`.
    This function does not support more customised operation like fitting an offset,
    but custom code can be easily written by copy/pasting from here.

    .. warning::
        If this function is used to plot the fit, beware that the fit is plotted using just
        two data-points if the axis is set to semilogy-scale
        (as the fit will be a straight line on that scale).

    Different modes are available to treat ``yerr``:

    *   ``"differentials"``: assume that ``yerr << ydata``, such that

        .. math::

            z &\equiv \ln y \\
            \delta z &= \left| \frac{\partial z}{\partial y} \right| \delta y \\
            \delta z &= \frac{\delta y}{y}

    .. seealso::

        `scipy.optimize.curve_fit
        <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html>`__

    :param xdata: Data points along the x-axis.
    :param ydata: Data points along the y-axis.
    :param yerr: Error-bar for ``ydata``.
    :param yerr_mode: How to treat the error in ``ydata``, see above.
    :param absolute_sigma: Treat (the effective) ``yerr`` as absolute error.
    :param prefactor: Prefactor :math:`c` (fitted if not specified).
    :param exponent: Exponent :math:`b` (fitted if not specified).

    :return:
        The fit details as a dictionary::

            prefactor: (Fitted) prefactor.
            exponent: (Fitted) exponent.
            prefactor_error: Estimated error of prefactor.
            exponent_error: Estimated error of exponent.
            pcov: Covariance of fit.
    """

    xdata = np.array(xdata)
    ydata = np.array(ydata)

    i = ydata > 0
    x = xdata[i]
    logy = np.log(ydata[i])

    j = np.logical_or(np.isnan(x), np.isnan(logy))
    logy = logy[~j]
    x = x[~j]

    fit_opts = {}

    if yerr is not None:
        if yerr_mode.lower() == "differentials":
            yerr = np.array(yerr)
            sigma = yerr[i][~j] / ydata[i][~j]
            sigma[yerr[i][~j] == 0] = np.finfo(sigma.dtype).eps  # avoid zero division
            fit_opts["sigma"] = sigma
            fit_opts["absolute_sigma"] = absolute_sigma
        else:
            raise OSError("yerr_mode: did you mean 'differentials'?")

    return _fit_loglog(x, logy, prefactor, exponent, **fit_opts)


def log(
    xdata: ArrayLike,
    ydata: ArrayLike,
    yerr: ArrayLike = None,
    **kwargs,
) -> dict:
    r"""
    Fit a logarithm :math:`y = a + b \ln x`.
    See documentation of :py:func:`linear`.
    """

    xdata = np.array(xdata)
    ydata = np.array(ydata)

    i = xdata > 0
    logx = np.log(xdata[i])
    y = ydata[i]
    if yerr is not None:
        yerr = yerr[i]

    j = np.isnan(logx)
    logx = logx[~j]
    y = y[~j]
    if yerr is not None:
        yerr = yerr[~j]

    return linear(logx, y, yerr, **kwargs)


def linear(
    xdata: ArrayLike,
    ydata: ArrayLike,
    yerr: ArrayLike = None,
    absolute_sigma: bool = True,
    offset: float = None,
    slope: float = None,
) -> dict:
    r"""
    Fit a linear function :math:`y = a + b x`.

    .. seealso::

        `scipy.optimize.curve_fit
        <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html>`__

    :param xdata: Data points along the x-axis.
    :param ydata: Data points along the y-axis.
    :param yerr: Error-bar for ``ydata``.
    :param absolute_sigma: Treat (the effective) ``yerr`` as absolute error.
    :param offset: Offset :math:`a` (fitted if not specified).
    :param slope: Slope :math:`b` (fitted if not specified).

    :return:
        The fit details as a dictionary::

            offset: (Fitted) offset.
            slope: (Fitted) slope.
            offset_error: Estimated error of offset.
            slope_error: Estimated error of slope.
            pcov: Covariance of fit.
    """

    xdata = np.array(xdata)
    ydata = np.array(ydata)

    fit_opts = {}
    details = {}

    if yerr is not None:
        sigma = np.array(yerr).astype(float)
        sigma[yerr == 0] = np.finfo(sigma.dtype).eps  # avoid zero division
        fit_opts["sigma"] = sigma
        fit_opts["absolute_sigma"] = absolute_sigma

    if offset is None and slope is None:

        def f(x, offset, slope):
            return offset + slope * x

        param, pcov = curve_fit(f, xdata, ydata, **fit_opts)
        offset = param[0]
        slope = param[1]
        details["offset_error"] = np.sqrt(pcov[0, 0])
        details["slope_error"] = np.sqrt(pcov[1, 1])

    elif offset is None:

        def f(x, offset):
            return offset + slope * x

        param, pcov = curve_fit(f, xdata, ydata, **fit_opts)
        offset = param[0]
        details["offset_error"] = np.sqrt(pcov[0, 0])
        details["slope_error"] = 0

    elif slope is None:

        def f(x, slope):
            return offset + slope * x

        param, pcov = curve_fit(f, xdata, ydata, **fit_opts)
        slope = param[0]
        details["offset_error"] = 0
        details["slope_error"] = np.sqrt(pcov[0, 0])

    details["offset"] = offset
    details["slope"] = slope

    return details
