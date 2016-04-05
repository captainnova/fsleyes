#!/usr/bin/env python
#
# lightboxopts.py - The LightBoxOpts class.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides the :class:`LightBoxOpts` class, which is used
by :class:`.LightBoxPanel` instances for managing their display settings.
"""


import logging
import copy

from . import sceneopts
from . import canvasopts


log = logging.getLogger(__name__)


class LightBoxOpts(sceneopts.SceneOpts):
    """The ``LightBoxOpts`` class contains display settings for the
    :class:`.LightBoxPanel` class.

    All of the properties in the ``LightBoxOpts`` class are defined in the
    :class:`.LightBoxCanvasOpts` class - see its documentation for more
    details.
    """

    sliceSpacing   = copy.copy(canvasopts.LightBoxCanvasOpts.sliceSpacing)
    zax            = copy.copy(canvasopts.LightBoxCanvasOpts.zax)
    ncols          = copy.copy(canvasopts.LightBoxCanvasOpts.ncols)
    nrows          = copy.copy(canvasopts.LightBoxCanvasOpts.nrows)
    topRow         = copy.copy(canvasopts.LightBoxCanvasOpts.topRow)
    zrange         = copy.copy(canvasopts.LightBoxCanvasOpts.zrange)
    showGridLines  = copy.copy(canvasopts.LightBoxCanvasOpts.showGridLines)
    highlightSlice = copy.copy(canvasopts.LightBoxCanvasOpts.highlightSlice)

    
    def __init__(self, *args, **kwargs):
        """Create a ``LightBoxOpts`` instance. All arguments are passed
        through to the :class:`.SceneOpts` constructor.

        The :attr:`.SceneOpts.zoom` attribute is modified, as
        :class:`LightBoxPanel` uses it slightly differently to the
        :class:`OrthoPanel`.
        """
        sceneopts.SceneOpts.__init__(self, *args, **kwargs)
        self.setConstraint('zoom', 'minval', 10)
        self.setConstraint('zoom', 'maxval', 1000)

        
    def _onPerformanceChange(self, *a):
        """Overrides :meth:`.SceneOpts._onPerformanceChange`. Changes the
        values of the :attr:`renderMode` and :attr:`resolutionLimit`
        properties according to the performance setting.
        """        

        if   self.performance == 4:
            self.renderMode      = 'onscreen'
            self.resolutionLimit = 0

        elif self.performance == 3:
            self.renderMode      = 'prerender'
            self.resolutionLimit = 0

        elif self.performance == 2:
            self.renderMode      = 'prerender'
            self.resolutionLimit = 1

        elif self.performance == 1:
            self.renderMode      = 'prerender'
            self.resolutionLimit = 2

        log.debug('Performance settings changed: '
                  'renderMode={}, '
                  'resolutionLimit={}'.format(
                      self.renderMode,
                      self.resolutionLimit))