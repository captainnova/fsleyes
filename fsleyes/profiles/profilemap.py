#!/usr/bin/env python
#
# profilemap.py - CanvasPanel -> Profile mappings.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module is used by the :class:`.Profile` and :class:`.ProfileManager`
classes.

It defines a few dictionaries which define the profile type to use for each
:class:`.ViewPanel` type, temporary mouse/keyboard interaction modes, and
alternate mode handlers for the profiles contained in the profiles package.

.. autosummary::
   profiles
   profileHandlers
   tempModeMap
   altHandlerMap
"""

import logging

from collections import OrderedDict

import wx

from fsleyes.views.orthopanel              import OrthoPanel
from fsleyes.views.lightboxpanel           import LightBoxPanel
from fsleyes.views.timeseriespanel         import TimeSeriesPanel
from fsleyes.views.histogrampanel          import HistogramPanel
from fsleyes.views.powerspectrumpanel      import PowerSpectrumPanel
from fsleyes.views.scene3dpanel            import Scene3DPanel

from fsleyes.profiles.orthoviewprofile     import OrthoViewProfile
from fsleyes.profiles.orthoeditprofile     import OrthoEditProfile
from fsleyes.profiles.orthocropprofile     import OrthoCropProfile
from fsleyes.profiles.orthoannotateprofile import OrthoAnnotateProfile
from fsleyes.profiles.lightboxviewprofile  import LightBoxViewProfile
from fsleyes.profiles.plotprofile          import PlotProfile
from fsleyes.profiles.histogramprofile     import HistogramProfile
from fsleyes.profiles.timeseriesprofile    import TimeSeriesProfile
from fsleyes.profiles.scene3dviewprofile   import Scene3DViewProfile


log = logging.getLogger(__name__)


profiles  = {
    OrthoPanel         : ['view', 'edit', 'crop', 'annotate'],
    LightBoxPanel      : ['view'],
    TimeSeriesPanel    : ['view'],
    HistogramPanel     : ['view'],
    PowerSpectrumPanel : ['view'],
    Scene3DPanel       : ['view'],
}
"""This dictionary is used by the :class:`.ProfileManager` to figure out which
profiles are available for each :class:`.ViewPanel`. They are added as options
to the :attr:`.ViewPanel.profile` property.
"""


profileHandlers = {
    (OrthoPanel,         'view')     : OrthoViewProfile,
    (OrthoPanel,         'edit')     : OrthoEditProfile,
    (OrthoPanel,         'crop')     : OrthoCropProfile,
    (OrthoPanel,         'annotate') : OrthoAnnotateProfile,
    (LightBoxPanel,      'view')     : LightBoxViewProfile,
    (TimeSeriesPanel,    'view')     : TimeSeriesProfile,
    (HistogramPanel,     'view')     : HistogramProfile,
    (PowerSpectrumPanel, 'view')     : PlotProfile,
    (Scene3DPanel,       'view')     : Scene3DViewProfile,
}
"""This dictionary is used by the :class:`.ProfileManager` class to figure out
which :class:`.Profile` sub-class to create for a given :class:`.ViewPanel`
instance and profile identifier.
"""


# Important: Any temporary modes which use CTRL,
# ALT, or CTRL+ALT must not handle character events,
# as these modifiers are reserved for global
# shortcuts.


# For multi-key combinations, the modifier key
# IDs must be provided as a tuple, in alphabetical
# order. For example, to specify shift+ctrl, the
# tuple must be (wx.WXK_CTRL, wx.WXK_SHIFT)
tempModeMap = {

    # Command/CTRL puts the user in zoom mode,
    # and ALT puts the user in pan mode
    OrthoViewProfile : OrderedDict((
        (('nav',   wx.WXK_CONTROL),                'zoom'),
        (('nav',   wx.WXK_ALT),                    'pan'),
        (('nav',   wx.WXK_SHIFT),                  'slice'),
        (('nav',  (wx.WXK_CONTROL, wx.WXK_SHIFT)), 'bricon'))),

    # OrthoEditProfile inherits all of the
    # settings for OrthoViewProfile above,
    # but overrides a few key ones.
    OrthoEditProfile : OrderedDict((

        (('sel',     wx.WXK_SHIFT),                  'slice'),
        (('desel',   wx.WXK_SHIFT),                  'slice'),
        (('selint',  wx.WXK_SHIFT),                  'slice'),
        (('fill',    wx.WXK_SHIFT),                  'slice'),
        (('sel',     wx.WXK_ALT),                    'pan'),
        (('desel',   wx.WXK_ALT),                    'pan'),
        (('selint',  wx.WXK_ALT),                    'pan'),
        (('fill',    wx.WXK_ALT),                    'pan'),
        (('sel',     wx.WXK_CONTROL),                'zoom'),
        (('desel',   wx.WXK_CONTROL),                'zoom'),
        (('selint',  wx.WXK_CONTROL),                'zoom'),
        (('fill',    wx.WXK_CONTROL),                'zoom'),
        (('sel',    (wx.WXK_CONTROL, wx.WXK_SHIFT)), 'chsize'),
        (('desel',  (wx.WXK_CONTROL, wx.WXK_SHIFT)), 'chsize'),
        (('selint', (wx.WXK_CONTROL, wx.WXK_SHIFT)), 'chthres'),
        (('selint', (wx.WXK_ALT,     wx.WXK_SHIFT)), 'chrad'))),

    OrthoCropProfile : OrderedDict((

        (('crop',  wx.WXK_SHIFT),                  'nav'),
        (('crop',  wx.WXK_CONTROL),                'zoom'),
        (('crop',  wx.WXK_ALT),                    'pan'),
        (('crop', (wx.WXK_CONTROL, wx.WXK_SHIFT)), 'slice'),
    )),

    OrthoAnnotateProfile : OrderedDict((

        (('line',     wx.WXK_SHIFT),                  'nav'),
        (('line',     wx.WXK_CONTROL),                'zoom'),
        (('line',     wx.WXK_ALT),                    'pan'),
        (('line',    (wx.WXK_CONTROL, wx.WXK_SHIFT)), 'slice'),
        (('point',    wx.WXK_SHIFT),                  'nav'),
        (('point',    wx.WXK_CONTROL),                'zoom'),
        (('point',    wx.WXK_ALT),                    'pan'),
        (('point',   (wx.WXK_CONTROL, wx.WXK_SHIFT)), 'slice'),
        (('rect',     wx.WXK_SHIFT),                  'nav'),
        (('rect',     wx.WXK_CONTROL),                'zoom'),
        (('rect',     wx.WXK_ALT),                    'pan'),
        (('rect',    (wx.WXK_CONTROL, wx.WXK_SHIFT)), 'slice'),
        (('text',     wx.WXK_SHIFT),                  'nav'),
        (('text',     wx.WXK_CONTROL),                'zoom'),
        (('text',     wx.WXK_ALT),                    'pan'),
        (('text',    (wx.WXK_CONTROL, wx.WXK_SHIFT)), 'slice'),
        (('ellipse',  wx.WXK_SHIFT),                  'nav'),
        (('ellipse',  wx.WXK_CONTROL),                'zoom'),
        (('ellipse',  wx.WXK_ALT),                    'pan'),
        (('ellipse', (wx.WXK_CONTROL, wx.WXK_SHIFT)), 'slice'),
        (('arrow',    wx.WXK_SHIFT),                  'nav'),
        (('arrow',    wx.WXK_CONTROL),                'zoom'),
        (('arrow',    wx.WXK_ALT),                    'pan'),
        (('arrow',   (wx.WXK_CONTROL, wx.WXK_SHIFT)), 'slice'),

    )),

    LightBoxViewProfile : OrderedDict((
        (('view', wx.WXK_CONTROL), 'zoom'), )),

    # Can't use shift on mpl
    # canvases for some reason.
    TimeSeriesProfile : OrderedDict((
        (('panzoom', wx.WXK_CONTROL), 'volume'),
    )),

    HistogramProfile : OrderedDict((
        (('panzoom', wx.WXK_CONTROL), 'overlayRange'),
    )),

    Scene3DViewProfile : OrderedDict((
        (('rotate', wx.WXK_CONTROL), 'zoom'),
        (('rotate', wx.WXK_ALT),     'pan'),
        (('rotate', wx.WXK_SHIFT),   'pick'),
    )),
}
"""The ``tempModeMap`` dictionary defines temporary modes, for each
:class:`Profile` sub-class which, when in a given mode, can be accessed with a
keyboard modifer (e.g. Control, Shift, etc). For example, a temporary mode map
of::

    ('view', wx.WXK_SHIFT) : 'zoom'

states that when the ``Profile`` is in ``'view'`` mode, and the shift key is
held down, the ``Profile`` should temporarily switch to ``'zoom'`` mode.
"""


altHandlerMap = {

    OrthoViewProfile : OrderedDict((

        # in navigate, slice, and zoom mode, the
        # left mouse button navigates, the right
        # mouse button draws a zoom rectangle,
        # and the middle button pans.
        (('nav',  'LeftMouseDown'),   ('nav',  'LeftMouseDrag')),
        (('nav',  'MiddleMouseDrag'), ('pan',  'LeftMouseDrag')),
        (('nav',  'RightMouseDown'),  ('zoom', 'RightMouseDown')),
        (('nav',  'RightMouseDrag'),  ('zoom', 'RightMouseDrag')),
        (('nav',  'RightMouseUp'),    ('zoom', 'RightMouseUp')),

        # In slice mode, the left and right
        # mouse buttons work as for pick mode.
        # Middle and right mouse works the
        # same as for nav mode, defined above.
        (('slice', 'LeftMouseDown'),   ('pick', 'LeftMouseDown')),
        (('slice', 'LeftMouseDrag'),   ('pick', 'LeftMouseDrag')),
        (('slice', 'MiddleMouseDrag'), ('pan',  'LeftMouseDrag')),
        (('slice', 'RightMouseDown'),  ('zoom', 'RightMouseDown')),
        (('slice', 'RightMouseDrag'),  ('zoom', 'RightMouseDrag')),
        (('slice', 'RightMouseUp'),    ('zoom', 'RightMouseUp')),

        # In zoom mode, the left mouse button
        # navigates, the right mouse button
        # draws a zoom rectangle, and the
        # middle mouse button pans
        (('zoom', 'RightMouseDown'),  ('zoom', 'RightMouseDrag')),
        (('zoom', 'LeftMouseDown'),   ('nav',  'LeftMouseDown')),
        (('zoom', 'LeftMouseDrag'),   ('nav',  'LeftMouseDrag')),
        (('zoom', 'MiddleMouseDrag'), ('pan',  'LeftMouseDrag')),

        # In pick mode, left mouse down
        # is the same as left mouse drag.
        (('pick', 'LeftMouseDown'),   ('pick', 'LeftMouseDrag')))),

    OrthoEditProfile : OrderedDict((

        # The OrthoEditProfile is in
        # 'nav' mode by default.

        # View keyboard navigation
        # works in major edit modes
        (('sel',    'Char'),  ('nav', 'Char')),
        (('desel',  'Char'),  ('nav', 'Char')),
        (('selint', 'Char'),  ('nav', 'Char')),
        (('fill',   'Char'),  ('nav', 'Char')),

        # When in select mode, the right
        # mouse button allows the user
        # to deselect voxels.
        (('sel',    'RightMouseDown'),  ('desel',  'LeftMouseDown')),
        (('sel',    'RightMouseDrag'),  ('desel',  'LeftMouseDrag')),
        (('sel',    'RightMouseUp'),    ('desel',  'LeftMouseUp')),

        # And vice versa
        (('desel',  'RightMouseDown'),  ('sel',    'LeftMouseDown')),
        (('desel',  'RightMouseDrag'),  ('sel',    'LeftMouseDrag')),
        (('desel',  'RightMouseUp'),    ('sel',    'LeftMouseUp')),

        # Right mouse alsi deselects in fill and selint mode
        (('fill',   'RightMouseDown'),  ('desel',  'LeftMouseDown')),
        (('fill',   'RightMouseDrag'),  ('desel',  'LeftMouseDrag')),
        (('fill',   'RightMouseUp'),    ('desel',  'LeftMouseUp')),

        (('selint', 'RightMouseDown'),  ('desel',  'LeftMouseDown')),
        (('selint', 'RightMouseDrag'),  ('desel',  'LeftMouseDrag')),
        (('selint', 'RightMouseUp'),    ('desel',  'LeftMouseUp')),

        # Make the selection cursor
        # visible in desel mode
        (('desel',  'MouseMove'),       ('sel',    'MouseMove')),

        # Middle mouse always pans.
        (('sel',    'MiddleMouseDrag'), ('pan', 'LeftMouseDrag')),
        (('desel',  'MiddleMouseDrag'), ('pan', 'LeftMouseDrag')),
        (('selint', 'MiddleMouseDrag'), ('pan', 'LeftMouseDrag')),
    )),

    OrthoCropProfile : OrderedDict((
        (('crop', 'MiddleMouseDrag'), ('pan', 'LeftMouseDrag')), )),

    OrthoAnnotateProfile : OrderedDict((
        (('line',    'MiddleMouseDrag'), ('pan', 'LeftMouseDrag')),
        (('point',   'MiddleMouseDrag'), ('pan', 'LeftMouseDrag')),
        (('rect',    'MiddleMouseDrag'), ('pan', 'LeftMouseDrag')),
        (('text',    'MiddleMouseDrag'), ('pan', 'LeftMouseDrag')),
        (('arrow',   'MiddleMouseDrag'), ('pan', 'LeftMouseDrag')),
        (('ellipse', 'MiddleMouseDrag'), ('pan', 'LeftMouseDrag')),

        # Right mouse click/drag allows
        # annotations to be moved
        (('line',    'RightMouseDown'),  ('move', 'RightMouseDown')),
        (('point',   'RightMouseDown'),  ('move', 'RightMouseDown')),
        (('rect',    'RightMouseDown'),  ('move', 'RightMouseDown')),
        (('text',    'RightMouseDown'),  ('move', 'RightMouseDown')),
        (('arrow',   'RightMouseDown'),  ('move', 'RightMouseDown')),
        (('ellipse', 'RightMouseDown'),  ('move', 'RightMouseDown')),

        (('line',    'RightMouseDrag'),  ('move', 'RightMouseDrag')),
        (('point',   'RightMouseDrag'),  ('move', 'RightMouseDrag')),
        (('rect',    'RightMouseDrag'),  ('move', 'RightMouseDrag')),
        (('text',    'RightMouseDrag'),  ('move', 'RightMouseDrag')),
        (('arrow',   'RightMouseDrag'),  ('move', 'RightMouseDrag')),
        (('ellipse', 'RightMouseDrag'),  ('move', 'RightMouseDrag')),

        (('line',    'RightMouseUp'),    ('move', 'RightMouseUp')),
        (('point',   'RightMouseUp'),    ('move', 'RightMouseUp')),
        (('rect',    'RightMouseUp'),    ('move', 'RightMouseUp')),
        (('text',    'RightMouseUp'),    ('move', 'RightMouseUp')),
        (('arrow',   'RightMouseUp'),    ('move', 'RightMouseUp')),
        (('ellipse', 'RightMouseUp'),    ('move', 'RightMouseUp')),
    )),

    LightBoxViewProfile : OrderedDict((
        (('view', 'LeftMouseDown'), ('view', 'LeftMouseDrag')), )),

    Scene3DViewProfile : OrderedDict((
        (('rotate', 'MiddleMouseDown'), ('pan', 'LeftMouseDown')),
        (('rotate', 'MiddleMouseDrag'), ('pan', 'LeftMouseDrag')),
        (('rotate', 'MiddleMouseUp'),   ('pan', 'LeftMouseUp')),
    )),


    # We cannot remap mouse buttons on the
    # PlotProfile.panzoom mode, because the
    # mpl NavigationToolbar2 class has
    # hard-coded left/right mouse button
    # behaviours.
}
"""The ``altHandlerMap`` dictionary defines alternate handlers for a given
mode and event type. Entries in this dictionary allow a :class:`.Profile`
sub-class to define a handler for a single mode and event type, but to re-use
that handler for other modes and event types. For example, the following
alternate handler mapping::

    ('zoom', 'MiddleMouseDrag'), ('pan',  'LeftMouseDrag'))

states that when the ``Profile`` is in ``'zoom'`` mode, and a
``MiddleMouseDrag`` event occurs, the ``LeftMouseDrag`` handler for the
``'pan'`` mode should be called.

.. note:: Event bindings defined in the ``altHandlerMap`` take precdence over
          the event bindings defined in the :class:`.Profile` sub-class. So
          you can use the ``altHandlerMap`` to override the default behaviour
          of a ``Profile``.
"""


fallbackHandlerMap = {
    OrthoViewProfile : OrderedDict((
        (('pick', 'LeftMouseDown'), ('nav', 'LeftMouseDown')),
        (('pick', 'LeftMouseDrag'), ('nav', 'LeftMouseDrag')),
    ))
}
"""The ``fallbackHandlerMap`` dictionary defines handlers for a given mode and
event type which will be called if the handler for that mode/event type returns
a value of ``False``, indicating that it has not been handled.
"""
