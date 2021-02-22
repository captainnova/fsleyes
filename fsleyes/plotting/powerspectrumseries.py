#!/usr/bin/env python
#
# powerspectrumseries.py - Classes used by the PowerSpectrumPanel.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides :class:`.DataSeries` sub-classes which are used
by the :class:`.PowerSpectrumPanel` for plotting power spectra.

The following classes are provided:

.. autosummary::
   :nosignatures:

   PowerSpectrumSeries
   VoxelPowerSpectrumSeries
   ComplexPowerSpectrumSeries
   ImaginaryPowerSpectrumSeries
   MagnitudePowerSpectrumSeries
   PhasePowerSpectrumSeries
   MelodicPowerSpectrumSeries
"""


import logging

import numpy     as np
import numpy.fft as fft

import fsl.data.image        as fslimage
import fsl.data.melodicimage as fslmelimage
import fsleyes_props         as props
import fsleyes.colourmaps    as fslcm
import fsleyes.strings       as strings
from . import                   dataseries


log = logging.getLogger(__name__)


def calcPowerSpectrum(data):
    """Calculates a power spectrum for the given one-dimensional data array.

    :arg data:    Numpy array containing the time series data

    :returns:     If ``data`` contains real values, the magnitude of the power
                  spectrum is returned. If ``data`` contains complex values,
                  the complex power spectrum is returned.
    """

    # Fourier transform on complex data
    if np.issubdtype(data.dtype, np.complexfloating):
        data = fft.fft(data)
        data = fft.fftshift(data)

    # Fourier transform on real data - we
    # calculate and return the magnitude.
    # We also drop the first (zero-frequency)
    # term (see the rfft docs) as it is
    # kind of useless for display purposes
    else:
        data = fft.rfft(data)[1:]
        data = magnitude(data)

    return data


def calcFrequencies(data, sampleTime):
    """Calculates the frequencies of the power spectrum for the given
    data.

    :arg data:       The input time series data
    :arg sampleTime: Time between each data point
    :returns:        A ``numpy`` array containing the frequencies of the
                     power spectrum for ``data``
    """

    nsamples = len(data)

    if np.issubdtype(data.dtype, np.complexfloating):
        xdata = fft.fftfreq(nsamples, sampleTime)
        xdata = fft.fftshift(xdata)
    else:
        # Drop the zero-frequency term
        # (see calcPowerSpectrum)
        xdata = fft.rfftfreq(nsamples, sampleTime)[1:]

    return xdata


def magnitude(data):
    """Returns the magnitude of the given complex data. """
    real  = data.real
    imag  = data.imag
    return np.sqrt(real ** 2 + imag ** 2)


def phase(data):
    """Returns the phase of the given complex data. """
    real = data.real
    imag = data.imag
    return np.arctan2(imag, real)


def normalise(data, dmin=None, dmax=None, nmin=0, nmax=1):
    """Returns ``data``, rescaled to the range [nmin, nmax].

    If dmin and dmax are provided, the data is normalised with respect to them,
    rather than being normalised by the data minimum/maximum.
    """
    if dmin is None: dmin = data.min()
    if dmax is None: dmax = data.max()
    return nmin + (nmax - nmin) * (data - dmin) / (dmax - dmin)


def phaseCorrection(spectrum, freqs, p0, p1):
    """Applies phase correction to the given complex power spectrum.

    :arg spectrum: Complex-valued power spectrum
    :arg freqs:    Spectrum frequency bins
    :arg p0:       Zero order phase correction term
    :arg p1:       First order phase correction term
    :returns:      The corrected power spectrum.
    """
    exp = 1j * 2 * np.pi * (p0 / 360 + freqs * p1)
    return np.exp(exp) * spectrum


class PowerSpectrumSeries:
    """The ``PowerSpectrumSeries`` encapsulates a power spectrum data series
    from an overlay. The ``PowerSpectrumSeries`` class is a base mixin class
    for all other classes in this module.
    """


    varNorm  = props.Boolean(default=False)
    """If ``True``, the fourier-transformed data is normalised to the range
    [0, 1] before plotting.

    .. note:: The :class:`ComplexPowerSpectrumSeries` applies normalisation
              differently.
    """


    @property
    def sampleTime(self):
        """Returns the time between time series samples for the overlay
        data. """
        if isinstance(self.overlay, fslmelimage.MelodicImage):
            return self.overlay.tr
        elif isinstance(self.overlay, fslimage.Image):
            return self.overlay.pixdim[3]
        else:
            return 1


class VoxelPowerSpectrumSeries(dataseries.VoxelDataSeries,
                               PowerSpectrumSeries):
    """The ``VoxelPowerSpectrumSeries`` class encapsulates the power spectrum
    of a single voxel from a 4D :class:`.Image` overlay. The voxel is dictated
    by the :attr:`.DisplayContext.location` property.
    """


    def __init__(self, *args, **kwargs):
        """Create a ``VoxelPowerSpectrumSeries``.  All arguments are passed
        to the :meth:`VoxelDataSeries.__init__` method. A :exc:`ValueError`
        is raised if the overlay is not a 4D :class:`.Image`.
        """

        dataseries.VoxelDataSeries.__init__(self, *args, **kwargs)

        if self.overlay.ndim < 4:
            raise ValueError('Overlay is not a 4D image')


    def getData(self):
        """Returns the data at the current voxel. """

        data = self.dataAtCurrentVoxel()

        if data is None:
            return None, None

        xdata = calcFrequencies(  data, self.sampleTime)
        ydata = calcPowerSpectrum(data)

        if self.varNorm:
            ydata = normalise(ydata)

        return xdata, ydata


class ComplexPowerSpectrumSeries(VoxelPowerSpectrumSeries):
    """This class is the frequency-spectrum equivalent of the
    :class:`.ComplexTimeSeries` class - see it for more details.
    """

    plotReal      = props.Boolean(default=True)
    plotImaginary = props.Boolean(default=False)
    plotMagnitude = props.Boolean(default=False)
    plotPhase     = props.Boolean(default=False)


    zeroOrderPhaseCorrection = props.Real(default=0)
    """Apply zero order phase correction to the power spectrum of the complex
    data.
    """


    firstOrderPhaseCorrection = props.Real(default=0)
    """Apply first order phase correction to the power spectrum of the complex
    data.
    """


    def __init__(self, overlay, overlayList, displayCtx, plotPanel):
        """Create a ``ComplexPowerSpectrumSeries``. All arguments are
        passed through to the :class:`VoxelPowerSpectrumSeries` constructor.
        """

        VoxelPowerSpectrumSeries.__init__(
            self, overlay, overlayList, displayCtx, plotPanel)

        self.__cachedData = (None, None)
        self.__imagps     = ImaginaryPowerSpectrumSeries(
            self, overlay, overlayList, displayCtx, plotPanel)
        self.__magps      = MagnitudePowerSpectrumSeries(
            self, overlay, overlayList, displayCtx, plotPanel)
        self.__phaseps    = PhasePowerSpectrumSeries(
            self, overlay, overlayList, displayCtx, plotPanel)

        for ps in (self.__imagps, self.__magps, self.__phaseps):
            ps.colour = fslcm.randomDarkColour()
            ps.bindProps('alpha',     self)
            ps.bindProps('lineWidth', self)
            ps.bindProps('lineStyle', self)


    def makeLabel(self):
        """Returns a string representation of this
        ``ComplexPowerSpectrumSeries`` instance.
        """
        return '{} ({})'.format(VoxelPowerSpectrumSeries.makeLabel(self),
                                strings.labels[self])


    @property
    def cachedData(self):
        """Returns the currently cached data (see :meth:`getData`). """
        return self.__cachedData


    def getData(self):
        """If :attr:`plotReal` is true, returns the real component of the power
        spectrum of the data at the current voxel. Otherwise returns ``(None,
        None)``.

        Every time this method is called, the power spectrum is calculated,
        phase correction is applied, and a reference to the resulting complex
        power spectrum (and frequencies) is saved; it is accessible via the
        :meth:`cachedData` property, for use by the
        :class:`ImaginaryPowerSpectrumSeries`,
        :class:`MagnitudePowerSpectrumSeries`, and
        :class:`PhasePowerSpectrumSeries`.
        """

        xdata, ydata = VoxelPowerSpectrumSeries.getData(self)

        if self.zeroOrderPhaseCorrection  != 0 or \
           self.firstOrderPhaseCorrection != 0:
            ydata = phaseCorrection(ydata,
                                    xdata,
                                    self.zeroOrderPhaseCorrection,
                                    self.firstOrderPhaseCorrection)

        # Note that we're assuming that this
        # ComplexPowerSpectrumSeries.getData
        # method will be called before the
        # corresponding call(s) to the
        # Imaginary/Magnitude/Phase series
        # methods.
        self.__cachedData = xdata, ydata

        if not self.plotReal:
            return None, None

        if ydata is not None:
            ydata = ydata.real

        return xdata, ydata


    def extraSeries(self):
        """Returns a list of additional series to be plotted, based
        on the values of the :attr:`plotImaginary`, :attr:`plotMagnitude`
        and :attr:`plotPhase` properties.
        """

        extras = []
        if self.plotImaginary: extras.append(self.__imagps)
        if self.plotMagnitude: extras.append(self.__magps)
        if self.plotPhase:     extras.append(self.__phaseps)
        return extras


class ImaginaryPowerSpectrumSeries(dataseries.DataSeries):
    """An ``ImaginaryPowerSpectrumSeries`` represents the power spectrum of the
    imaginary component of a complex-valued image.
    ``ImaginaryPowerSpectrumSeries`` instances are created by
    :class:`ComplexPowerSpectrumSeries` instances.
    """


    def __init__(self, parent, *args, **kwargs):
        """Create an ``ImaginaryPowerSpectrumSeries``.

        :arg parent: The :class:`ComplexPowerSpectrumSeries` which owns this
                     ``ImaginaryPowerSpectrumSeries``.

        All other arguments are passed through to the :class:`DataSeries`
        constructor.
        """
        dataseries.DataSeries.__init__(self, *args, **kwargs)
        self.__parent = parent


    def makeLabel(self):
        """Returns a string representation of this
        ``ImaginaryPowerSpectrumSeries`` instance.
        """
        return '{} ({})'.format(self.__parent.makeLabel(),
                                strings.labels[self])


    def getData(self):
        """Returns the imaginary component of the power spectrum. """

        xdata, ydata = self.__parent.cachedData

        if ydata is not None:
            ydata = ydata.imag

        return xdata, ydata


class MagnitudePowerSpectrumSeries(dataseries.DataSeries):
    """An ``MagnitudePowerSpectrumSeries`` represents the magnitude of a
    complex-valued image. ``MagnitudePowerSpectrumSeries`` instances are
    created by :class:`ComplexPowerSpectrumSeries` instances.
    """


    def __init__(self, parent, *args, **kwargs):
        """Create an ``ImaginaryPowerSpectrumSeries``.

        :arg parent: The :class:`ComplexPowerSpectrumSeries` which owns this
                     ``ImaginaryPowerSpectrumSeries``.

        All other arguments are passed through to the :class:`DataSeries`
        constructor.
        """
        dataseries.DataSeries.__init__(self, *args, **kwargs)
        self.__parent = parent


    def makeLabel(self):
        """Returns a string representation of this
        ``MagnitudePowerSpectrumSeries`` instance.
        """
        return '{} ({})'.format(self.__parent.makeLabel(),
                                strings.labels[self])


    def getData(self):
        """Returns the magnitude of the complex power spectrum. """
        xdata, ydata = self.__parent.cachedData
        if ydata is not None:
            ydata = magnitude(ydata)
        return xdata, ydata


class PhasePowerSpectrumSeries(dataseries.DataSeries):
    """An ``PhasePowerSpectrumSeries`` represents the phase of a complex-valued
    image. ``PhasePowerSpectrumSeries`` instances are created by
    :class:`ComplexPowerSpectrumSeries` instances.
    """


    def __init__(self, parent, *args, **kwargs):
        """Create an ``ImaginaryPowerSpectrumSeries``.

        :arg parent: The :class:`ComplexPowerSpectrumSeries` which owns this
                     ``ImaginaryPowerSpectrumSeries``.

        All other arguments are passed through to the :class:`DataSeries`
        constructor.
        """
        dataseries.DataSeries.__init__(self, *args, **kwargs)
        self.__parent = parent


    def makeLabel(self):
        """Returns a string representation of this ``PhasePowerSpectrumSeries``
        instance.
        """
        return '{} ({})'.format(self.__parent.makeLabel(),
                                strings.labels[self])


    def getData(self):
        """Returns the phase of the complex power spectrum. """
        xdata, ydata = self.__parent.cachedData
        if ydata is not None:
            ydata = phase(ydata)
        return xdata, ydata


class MelodicPowerSpectrumSeries(dataseries.DataSeries,
                                 PowerSpectrumSeries):
    """The ``MelodicPowerSpectrumSeries`` class encapsulates the power spectrum
    of the time course for a single component of a :class:`.MelodicImage`. The
    component is dictated by the :attr:`.NiftiOpts.volume` property.
    """


    def __init__(self, *args, **kwargs):
        """Create a ``MelodicPowerSpectrumSeries``. All arguments are passed
        through to the :meth:`PowerSpectrumSeries.__init__` method.
        """
        dataseries.DataSeries.__init__(self, *args, **kwargs)

        if not isinstance(self.overlay, fslmelimage.MelodicImage):
            raise ValueError('Overlay is not a MelodicImage')

        self.varNorm = False
        self.disableProperty('varNorm')


    def makeLabel(self):
        """Returns a label that can be used for this
        ``MelodicPowerSpectrumSeries``.
        """
        display   = self.displayCtx.getDisplay(self.overlay)
        opts      = display.opts
        component = opts.volume

        return '{} [component {}]'.format(display.name, component + 1)


    def getData(self):
        """Returns the power spectrum for the current component of the
        :class:`.MelodicImage`, as defined by the :attr:`.NiftiOpts.volume`
        property.
        """

        opts      = self.displayCtx.getOpts(self.overlay)
        component = opts.volume

        ydata = self.overlay.getComponentPowerSpectrum(component)
        xdata = np.arange(len(ydata), dtype=np.float32)

        return xdata, ydata


class MeshPowerSpectrumSeries(dataseries.DataSeries,
                              PowerSpectrumSeries):
    """A ``MeshPowerSpectrumSeries`` object encapsulates the power spectrum for
    the data from a :class:`.Mesh` overlay which has some time series
    vertex data associated with it. See the :attr:`.MeshOpts.vertexData`
    property.
    """


    def __init__(self, *args, **kwargs):
        """Create a ``MeshPowerSpectrumSeries`` instance. All arguments are
        passed through to  :meth:`.DataSeries.__init__`.
        """
        dataseries.DataSeries.__init__(self, *args, **kwargs)


    def makeLabel(self):
        """Returns a label to use for this ``MeshPowerSpectrumSeries`` on the
        legend.
        """

        display = self.displayCtx.getDisplay(self.overlay)

        if self.__haveData():
            opts = display.opts
            vidx = opts.getVertex()
            return '{} [{}]'.format(display.name, vidx)

        else:
            return display.name


    def __haveData(self):
        """Returns ``True`` if there is currently time series data to show
        for this ``MeshPowerSpectrumSeries``, ``False`` otherwise.
        """
        opts = self.displayCtx.getOpts(self.overlay)
        vidx = opts.getVertex()
        vd   = opts.getVertexData()

        return vidx is not None and vd is not None and vd.shape[1] > 1


    def getData(self):
        """Returns the power spectrum of the data at the current location for
        the :class:`.Mesh`, or ``None, None`` if there is no data.
        """

        if not self.__haveData():
            return None, None

        opts = self.displayCtx.getOpts(self.overlay)
        vidx = opts.getVertex()

        if vidx is None:
            return None, None

        vd    = opts.getVertexData()
        data  = vd[vidx, :]
        xdata = calcFrequencies(  data, self.sampleTime)
        ydata = calcPowerSpectrum(data, self.varNorm)

        return xdata, ydata
