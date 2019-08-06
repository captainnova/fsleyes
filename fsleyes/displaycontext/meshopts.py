#!/usr/bin/env python
#
# meshopts.py - The MeshOpts class.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides the :class:`MeshOpts` class, which defines settings
for displaying :class:`.Mesh` overlays.
"""


import logging

import numpy as np

import fsl.data.image       as fslimage
import fsl.data.utils       as dutils
import fsl.utils.transform  as transform
import fsl.utils.deprecated as deprecated
import fsleyes_props        as props

import fsleyes.colourmaps   as colourmaps
import fsleyes.overlay      as fsloverlay
import fsleyes.colourmaps   as fslcmaps
from . import display       as fsldisplay
from . import colourmapopts as cmapopts


log = logging.getLogger(__name__)


def genMeshColour(overlay):
    """Called by :meth:`MeshOpts.__init__`. Generates an initial colour for
    the given :class:`.Mesh` overlay.

    If the overlay file name looks like it was generated by the FSL FIRST
    segmentation tool, returns a colour from the ``freesurfercolorlut`` colour
    map. Otherwise returns a random colour.
    """
    filename        = str(overlay.dataSource)
    subcorticalCmap = colourmaps.getLookupTable('freesurfercolorlut')

    if   'L_Thal' in filename: return subcorticalCmap.get(10).colour
    elif 'L_Caud' in filename: return subcorticalCmap.get(11).colour
    elif 'L_Puta' in filename: return subcorticalCmap.get(12).colour
    elif 'L_Pall' in filename: return subcorticalCmap.get(13).colour
    elif 'BrStem' in filename: return subcorticalCmap.get(16).colour
    elif 'L_Hipp' in filename: return subcorticalCmap.get(17).colour
    elif 'L_Amyg' in filename: return subcorticalCmap.get(18).colour
    elif 'L_Accu' in filename: return subcorticalCmap.get(26).colour
    elif 'R_Thal' in filename: return subcorticalCmap.get(49).colour
    elif 'R_Caud' in filename: return subcorticalCmap.get(50).colour
    elif 'R_Puta' in filename: return subcorticalCmap.get(51).colour
    elif 'R_Pall' in filename: return subcorticalCmap.get(52).colour
    elif 'R_Hipp' in filename: return subcorticalCmap.get(53).colour
    elif 'R_Amyg' in filename: return subcorticalCmap.get(54).colour
    elif 'R_Accu' in filename: return subcorticalCmap.get(58).colour

    return colourmaps.randomBrightColour()


class MeshOpts(cmapopts.ColourMapOpts, fsldisplay.DisplayOpts):
    """The ``MeshOpts`` class defines settings for displaying :class:`.Mesh`
    overlays. See also the :class:`.GiftiOpts` and :class:`.FreesurferOpts`
    sub-classes.
    """


    colour = props.Colour()
    """The mesh colour. """


    outline = props.Boolean(default=False)
    """If ``True``, an outline of the mesh is shown. Otherwise a
    cross- section of the mesh is filled.
    """


    outlineWidth = props.Real(minval=0.1, maxval=10, default=2, clamped=False)
    """If :attr:`outline` is ``True``, this property defines the width of the
    outline in pixels.
    """


    showName = props.Boolean(default=False)
    """If ``True``, the mesh name is shown alongside it.

    .. note:: Not implemented yet, and maybe never will be.
    """


    discardClipped = props.Boolean(default=False)
    """Flag which controls clipping. When the mesh is coloured according to
    some data (the :attr:`vertexData` property), vertices with a data value
    outside of the clipping range are either discarded (not drawn), or
    they are still drawn, but not according to the data, rather with the
    flat :attr:`colour`.
    """


    vertexSet = props.Choice((None, ))
    """May be populated with the names of files which contain different
    vertex sets for the :class:`.Mesh` object.
    """


    vertexData = props.Choice((None, ))
    """May be populated with the names of files which contain data associated
    with each vertex in the mesh, that can be used to colour the mesh. When
    some vertex data has been succsessfully loaded, it can be accessed via
    the :meth:`getVertexData` method.
    """


    vertexDataIndex = props.Int(minval=0, maxval=0, default=0, clamped=True)
    """If :attr:`vertexData` is loaded, and has multiple data points per
    vertex (e.g. time series), this property controls the index into the
    data.
    """


    refImage = props.Choice()
    """A reference :class:`.Image` instance which the mesh coordinates are
    in terms of.

    For example, if this :class:`.Mesh` represents the segmentation of
    a sub-cortical region from a T1 image, you would set the ``refImage`` to
    that T1 image.

    Any :class:`.Image` instance in the :class:`.OverlayList` may be chosen
    as the reference image.
    """


    useLut = props.Boolean(default=False)
    """If ``True``, and if some :attr:`vertexData` is loaded, the :attr:`lut`
    is used to colour vertex values instead of the :attr:`cmap` and
    :attr:`negativeCmap`.
    """


    lut = props.Choice()
    """If :attr:`useLut` is ``True``, a :class:`.LookupTable` is used to
    colour vertex data instead of the :attr:`cmap`/:attr:`negativeCmap`.
    """


    # This property is implicitly tightly-coupled to
    # the NiftiOpts.getTransform method - the choices
    # defined in this property are assumed to be valid
    # inputs to that method (with the exception of
    # ``'torig'``).
    coordSpace = props.Choice(('torig', 'affine', 'pixdim', 'pixdim-flip',
                               'id'),
                              default='pixdim-flip')
    """If :attr:`refImage` is not ``None``, this property defines the
    reference image coordinate space in which the mesh coordinates are
    defined (i.e. voxels, scaled voxels, or world coordinates).

    =============== =========================================================
    ``affine``      The mesh coordinates are defined in the reference image
                    world coordinate system.

    ``torig``       Equivalent to ``'affine'``, except for
                    :class:`.FreesurferOpts`  sub-classes.

    ``id``          The mesh coordinates are defined in the reference image
                    voxel coordinate system.

    ``pixdim``      The mesh coordinates are defined in the reference image
                    voxel coordinate system, scaled by the voxel pixdims.

    ``pixdim-flip`` The mesh coordinates are defined in the reference image
                    voxel coordinate system, scaled by the voxel pixdims. If
                    the reference image transformation matrix has a positive
                    determinant, the X axis is flipped.
    =============== =========================================================

    The default value is ``pixdim-flip``, as this is the coordinate system
    used in the VTK sub-cortical segmentation model files output by FIRST.
    See also the :ref:`note on coordinate systems
    <volumeopts-coordinate-systems>`, and the :meth:`.NiftiOpts.getTransform`
    method.
    """


    wireframe = props.Boolean(default=False)
    """3D only. If ``True``, the mesh is rendered as a wireframe. """


    def __init__(self, overlay, *args, **kwargs):
        """Create a ``MeshOpts`` instance.

        :arg useTorig: If ``False`` (the default), the ``'torig'`` option
                       from the :attr:`coordSpace` property is removed.

        All other arguments are passed through to the :class:`.DisplayOpts`
        constructor.
        """

        useTorig = kwargs.pop('useTorig', False)

        if not useTorig:
            self.getProp('coordSpace').removeChoice('torig', instance=self)

        # Set a default colour
        colour      = genMeshColour(overlay)
        self.colour = np.concatenate((colour, [1.0]))

        # ColourMapOpts.linkLowRanges defaults to
        # True, which is annoying for surfaces.
        self.linkLowRanges = False

        # A copy of the refImage property
        # value is kept here so, when it
        # changes, we can de-register from
        # the previous one.
        self.__oldRefImage = None

        # When the vertexData property is
        # changed, the data (and its min/max)
        # is loaded and stored in these
        # attributes. See the __vertexDataChanged
        # method.
        self.__vertexData      = None
        self.__vertexDataRange = None

        nounbind = kwargs.get('nounbind', [])
        nounbind.extend(['refImage', 'coordSpace', 'vertexData', 'vertexSet'])
        kwargs['nounbind'] = nounbind

        fsldisplay.DisplayOpts  .__init__(self, overlay, *args, **kwargs)
        cmapopts  .ColourMapOpts.__init__(self)

        self.__registered = self.getParent() is not None

        # Load all vertex data and vertex
        # sets on the parent opts instance
        if not self.__registered:
            self.addVertexSetOptions( overlay.vertexSets())
            self.addVertexDataOptions(overlay.vertexDataSets())

        # The master MeshOpts instance is just a
        # sync-slave, so we only need to register
        # property listeners on child instances
        else:

            self.overlayList.addListener('overlays',
                                         self.name,
                                         self.__overlayListChanged,
                                         immediate=True)

            self.addListener('refImage',
                             self.name,
                             self.__refImageChanged,
                             immediate=True)
            self.addListener('coordSpace',
                             self.name,
                             self.__coordSpaceChanged,
                             immediate=True)

            # We need to keep colour[3]
            # keeps colour[3] and Display.alpha
            # consistent w.r.t. each other (see
            # also MaskOpts)
            self.display.addListener('alpha',
                                     self.name,
                                     self.__alphaChanged,
                                     immediate=True)
            self        .addListener('colour',
                                     self.name,
                                     self.__colourChanged,
                                     immediate=True)

            self.addListener('vertexData',
                             self.name,
                             self.__vertexDataChanged,
                             immediate=True)
            self.addListener('vertexSet',
                             self.name,
                             self.__vertexSetChanged,
                             immediate=True)
            overlay.register(self.name,
                             self.__overlayVerticesChanged,
                             'vertices')

            self.__overlayListChanged()
            self.__updateBounds()

        # If we have inherited values from a
        # parent instance, make sure the vertex
        # data (if set) is initialised
        self.__vertexDataChanged()

        # If a reference image has not
        # been set on the parent MeshOpts
        # instance, see  if there is a
        # suitable one in the overlay list.
        if self.refImage is None:
            self.refImage = fsloverlay.findMeshReferenceImage(
                self.overlayList, self.overlay)


    def destroy(self):
        """Removes some property listeners, and calls the
        :meth:`.DisplayOpts.destroy` method.
        """

        if self.__registered:

            self.overlayList.removeListener('overlays', self.name)
            self.display    .removeListener('alpha',    self.name)
            self            .removeListener('colour',   self.name)
            self.overlay    .deregister(self.name, 'vertices')

            for overlay in self.overlayList:

                # An error could be raised if the
                # DC has been/is being destroyed
                try:

                    display = self.displayCtx.getDisplay(overlay)
                    opts    = self.displayCtx.getOpts(   overlay)

                    display.removeListener('name', self.name)

                    if overlay is self.refImage:
                        opts.removeListener('transform', self.name)

                except Exception:
                    pass

        self.__oldRefImage = None
        self.__vertexData  = None

        cmapopts  .ColourMapOpts.destroy(self)
        fsldisplay.DisplayOpts  .destroy(self)


    @classmethod
    def getVolumeProps(cls):
        """Overrides :meth:`DisplayOpts.getVolumeProps`. Returns a list
        of property names which control the displayed volume/timepoint.
        """
        return ['vertexDataIndex']


    def getDataRange(self):
        """Overrides the :meth:`.ColourMapOpts.getDisplayRange` method.
        Returns the display range of the currently selected
        :attr:`vertexData`, or ``(0, 1)`` if none is selected.
        """
        if self.__vertexDataRange is None: return (0, 1)
        else:                              return self.__vertexDataRange


    def getVertexData(self):
        """Returns the :attr:`.MeshOpts.vertexData`, if some is loaded.
        Returns ``None`` otherwise.
        """
        return self.__vertexData


    def vertexDataLen(self):
        """Returns the length (number of data points per vertex) of the
        currently selected :attr:`vertexData`, or ``0`` if no vertex data is
        selected.
        """

        if self.__vertexData is None:
            return 0

        elif len(self.__vertexData.shape) == 1:
            return 1

        else:
            return self.__vertexData.shape[1]


    def addVertexDataOptions(self, paths):
        """Adds the given sequence of paths as options to the
        :attr:`vertexData` property. It is assumed that the paths refer
        to valid vertex data files for the overlay associated with this
        ``MeshOpts`` instance.
        """

        vdataProp = self.getProp('vertexData')
        newPaths  = paths
        paths     = vdataProp.getChoices(instance=self)
        paths     = paths + [p for p in newPaths if p not in paths]

        vdataProp.setChoices(paths, instance=self)


    def addVertexSetOptions(self, paths):
        """Adds the given sequence of paths as options to the
        :attr:`vertexSet` property. It is assumed that the paths refer
        to valid vertex files for the overlay associated with this
        ``MeshOpts`` instance.
        """

        vsetProp = self.getProp('vertexSet')
        newPaths = paths
        paths    = vsetProp.getChoices(instance=self)
        paths    = paths + [p for p in newPaths if p not in paths]

        vsetProp.setChoices(paths, instance=self)


    def getConstantColour(self):
        """Returns the current :attr::`colour`, adjusted according to the
        current :attr:`.Display.brightness`, :attr:`.Display.contrast`, and
        :attr:`.Display.alpha`.
        """

        display = self.display

        # Only apply bricon if there is no vertex data assigned
        if self.vertexData is None:
            brightness = display.brightness / 100.0
            contrast   = display.contrast   / 100.0
        else:
            brightness = 0.5
            contrast   = 0.5

        colour = list(fslcmaps.applyBricon(
            self.colour[:3], brightness, contrast))

        colour.append(display.alpha / 100.0)

        return colour


    @property
    def referenceImage(self):
        """Overrides :meth:`.DisplayOpts.referenceImage`.

        If a :attr:`refImage` is selected, it is returned. Otherwise,``None``
        is returned.
        """
        return self.refImage


    @deprecated.deprecated('0.22.3', '1.0.0', 'Use getTransform instead')
    def getCoordSpaceTransform(self):
        """Returns a transformation matrix which can be used to transform
        the :class:`.Mesh` vertex coordinates into the display
        coordinate system.

        If no :attr:`refImage` is selected, this method returns an identity
        transformation.
        """

        if self.refImage is None or self.refImage not in self.overlayList:
            return np.eye(4)

        opts = self.displayCtx.getOpts(self.refImage)

        return opts.getTransform(self.coordSpace, opts.transform)


    def getVertex(self, xyz=None):
        """Returns an integer identifying the index of the mesh vertex that
        coresponds to the given ``xyz`` location, assumed to be specified
        in the display coordinate system.

        :arg xyz: Location to convert to a vertex index. If not provided, the
                  current :class:`.DisplayContext.location` is used.
        """

        # TODO return vertex closest to the point,
        #      within some configurabe tolerance?
        if xyz is None:
            xyz = self.displayCtx.location

        xyz  = self.transformCoords(xyz, 'display', 'mesh')
        xyz  = np.asarray(xyz).reshape(1, 3)
        vidx = self.overlay.trimesh.nearest.vertex(xyz)[1][0]

        return vidx


    def normaliseSpace(self, space):
        """Used by :meth:`transformCoords` and :meth:`getTransform` to
        normalise their ``from_`` and ``to`` parameters.
        """
        if space not in ('world', 'display', 'mesh'):
            raise ValueError('Invalid space: {}'.format(space))

        if space == 'mesh':  space = self.coordSpace
        if space == 'torig': space = 'affine'

        return space


    def transformCoords(self, coords, from_, to, *args, **kwargs):
        """Transforms the given ``coords`` from ``from_`` to ``to``.

        :arg coords: Coordinates to transform.
        :arg from_:  Space that the coordinates are in
        :arg to:     Space to transform the coordinates to

        All other parameters are passed through to the
        :meth:`.NiftiOpts.transformCoords` method of the reference image
        ``DisplayOpts``.

        The following values are accepted for the ``from_`` and ``to``
        parameters:

          - ``'world'``:  World coordinate system
          - ``'display'`` Display coordinate system
          - ``'mesh'``    The coordinate system of this mesh.
        """

        from_ = self.normaliseSpace(from_)
        to    = self.normaliseSpace(to)

        if self.refImage is None:
            return coords

        opts = self.displayCtx.getOpts(self.refImage)

        return opts.transformCoords(coords, from_, to, *args, **kwargs)


    def getTransform(self, from_, to):
        """Return a matrix which may be used to transform coordinates from
        ``from_`` to ``to``.

        The following values are accepted for the ``from_`` and ``to``
        parameters:

          - ``'world'``:  World coordinate system
          - ``'display'`` Display coordinate system
          - ``'mesh'``    The coordinate system of this mesh.
        """

        from_ = self.normaliseSpace(from_)
        to    = self.normaliseSpace(to)

        if self.refImage is None:
            return np.eye(4)

        opts = self.displayCtx.getOpts(self.refImage)

        return opts.getTransform(from_, to)


    def __transformChanged(self, value, valid, ctx, name):
        """Called when the :attr:`.NiftiOpts.transform` property of the current
        :attr:`refImage` changes. Calls :meth:`__updateBounds`.
        """
        self.__updateBounds()


    def __coordSpaceChanged(self, *a):
        """Called when the :attr:`coordSpace` property changes.
        Calls :meth:`__updateBounds`.
        """
        self.__updateBounds()


    def __refImageChanged(self, *a):
        """Called when the :attr:`refImage` property changes.

        If a new reference image has been specified, removes listeners from
        the old one (if necessary), and adds listeners to the
        :attr:`.NiftiOpts.transform` property associated with the new image.
        Calls :meth:`__updateBounds`.
        """

        # TODO You are not tracking changes to the
        # refImage overlay type -  if this changes,
        # you will need to re-bind to the transform
        # property of the new DisplayOpts instance

        if self.__oldRefImage is not None and \
           self.__oldRefImage in self.overlayList:

            opts = self.displayCtx.getOpts(self.__oldRefImage)
            opts.removeListener('transform', self.name)

        self.__oldRefImage = self.refImage

        if self.refImage is not None:
            opts = self.displayCtx.getOpts(self.refImage)
            opts.addListener('transform',
                             self.name,
                             self.__transformChanged,
                             immediate=True)

        self.__updateBounds()


    def __updateBounds(self):
        """Called whenever any of the :attr:`refImage`, :attr:`coordSpace`,
        or :attr:`transform` properties change.

        Updates the :attr:`.DisplayOpts.bounds` property accordingly.
        """

        lo, hi = self.overlay.bounds
        xform  = self.getTransform('mesh', 'display')
        lohi   = transform.transform([lo, hi], xform)
        lohi.sort(axis=0)
        lo, hi = lohi[0, :], lohi[1, :]

        oldBounds = self.bounds
        self.bounds = [lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]]

        if np.all(np.isclose(oldBounds, self.bounds)):
            self.propNotify('bounds')


    def __overlayListChanged(self, *a):
        """Called when the overlay list changes. Updates the :attr:`refImage`
        property so that it contains a list of overlays which can be
        associated with the mesh.
        """

        imgProp  = self.getProp('refImage')
        imgVal   = self.refImage
        overlays = self.displayCtx.getOrderedOverlays()

        # the overlay for this MeshOpts
        # instance has been removed
        if self.overlay not in overlays:
            self.overlayList.removeListener('overlays', self.name)
            return

        imgOptions = [None]

        for overlay in overlays:

            # The overlay must be a Nifti instance.
            if not isinstance(overlay, fslimage.Nifti):
                continue

            imgOptions.append(overlay)

            display = self.displayCtx.getDisplay(overlay)
            display.addListener('name',
                                self.name,
                                self.__overlayListChanged,
                                overwrite=True)

        # The previous refImage may have
        # been removed from the overlay list
        if imgVal in imgOptions: self.refImage = imgVal
        else:                    self.refImage = None

        imgProp.setChoices(imgOptions, instance=self)


    def __overlayVerticesChanged(self, *a):
        """Called when the :attr:`.Mesh.vertices` change. Makes sure that the
        :attr:`vertexSet` attribute is synchronised.
        """

        vset   = self.overlay.selectedVertices()
        vsprop = self.getProp('vertexSet')

        if vset not in vsprop.getChoices(instance=self):
            self.addVertexSetOptions([vset])
        self.vertexSet = vset


    def __vertexSetChanged(self, *a):
        """Called when the :attr:`.MeshOpts.vertexSet` property changes.
        Updates the current vertex set on the :class:`.Mesh` overlay, and
        the overlay bounds.
        """

        if self.vertexSet not in self.overlay.vertexSets():
            self.overlay.loadVertices(self.vertexSet)
        else:
            with self.overlay.skip(self.name, 'vertices'):
                self.overlay.vertices = self.vertexSet

        self.__updateBounds()


    def __vertexDataChanged(self, *a):
        """Called when the :attr:`vertexData` property changes. Attempts to
        load the data if possible. The data may subsequently be retrieved
        via the :meth:`getVertexData` method.
        """

        vdata      = None
        vdataRange = None
        overlay    = self.overlay
        vdfile     = self.vertexData

        try:
            if vdfile is not None:

                if vdfile not in overlay.vertexDataSets():
                    log.debug('Loading vertex data: {}'.format(vdfile))
                    vdata = overlay.loadVertexData(vdfile)
                else:
                    vdata = overlay.getVertexData(vdfile)

                vdataRange = np.nanmin(vdata), np.nanmax(vdata)

                if len(vdata.shape) == 1:
                    vdata = vdata.reshape(-1, 1)

                vdata = dutils.makeWriteable(vdata)

        except Exception as e:

            # TODO show a warning
            log.warning('Unable to load vertex data from {}: {}'.format(
                vdfile, e, exc_info=True))

            vdata      = None
            vdataRange = None

        self.__vertexData      = vdata
        self.__vertexDataRange = vdataRange

        if vdata is not None: npoints = vdata.shape[1]
        else:                 npoints = 1

        self.vertexDataIndex = 0
        self.setAttribute('vertexDataIndex', 'maxval', npoints - 1)

        self.updateDataRange()


    def __colourChanged(self, *a):
        """Called when :attr:`.colour` changes. Updates :attr:`.Display.alpha`
        from the alpha component.
        """

        alpha = self.colour[3] * 100

        log.debug('Propagating MeshOpts.colour[3] to '
                  'Display.alpha [{}]'.format(alpha))

        with props.skip(self.display, 'alpha', self.name):
            self.display.alpha = alpha


    def __alphaChanged(self, *a):
        """Called when :attr:`.Display.alpha` changes. Updates the alpha
        component of :attr:`.colour`.
        """

        alpha      = self.display.alpha / 100.0
        r, g, b, _ = self.colour

        log.debug('Propagating Display.alpha to MeshOpts.'
                  'colour[3] [{}]'.format(alpha))

        with props.skip(self, 'colour', self.name):
            self.colour = r, g, b, alpha
