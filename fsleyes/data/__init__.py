#!/usr/bin/env python
#
# __init__.py - FSLeyes overlay types and data-related utilities.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""The :mod:`fsleyes.data` module contains FSLeyes overlay data types and
some data-related utilities.

Most FSLeyes overlay data types are defined in the ``fslpy`` library
(e.g. :class:`fsl.data.image.Image`, :class:`fsl.data.mesh.Mesh`). This
sub-package provides some additional overlay types that can be displayed with
FSLeyes:

.. autosummary::
   :nosignatures:

   ~fsleyes.data.tractogram.Tractogram
"""

import os.path as op

import fsl.utils.path          as fslpath
import fsl.data.utils          as dutils
import fsl.data.image          as fslimage
import fsleyes.data.tractogram as tractogram
import fsleyes.displaycontext  as fsldisplay


def guessType(path):
    """Wrapper around the :func:`fsl.data.utils.guessType` function from the
    ``fslpy`` library, augmented to support additional data types supported
    by FSLeyes.

    :arg path: Path to a file to be loaded
    :returns:  Tuple containing:

               - A data type which can be used to load the file, or ``None``
                 if the file is not recognised.
               - A suitable value for the :meth:`.Display.overlayType` for
                 the file, or ``None`` if the file type is not recognised.
               - The file path, possibly modified (e.g. made absolute).
    """

    path  = op.abspath(path)
    dtype = None
    otype = None

    if op.isfile(path):
        if fslpath.hasExt(path.lower(), tractogram.ALLOWED_EXTENSIONS):
            dtype = tractogram.Tractogram

    if dtype is None:
        dtype, path = dutils.guessType(path)

    # We need to peek at some images in order
    # to determine a suitable overlay type
    # (e.g. complex images -> "complex")
    if dtype is fslimage.Image:
        img   = fslimage.Image(path)
        otype = fsldisplay.getOverlayTypes(img)[0]
    elif dtype is not None:
        otype = fsldisplay.OVERLAY_TYPES[dtype][0]

    return dtype, otype, path
