#!/usr/bin/env python
#
# test_overlay_freesurfermesh.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import os.path as op

import pytest

import nibabel as nib
import fsl.data.image as fslimage

from . import run_cli_tests


pytestmark = pytest.mark.overlayclitest


cli_tests = """
freesurfer/lh.pial -mc 1 0 0
freesurfer/lh.pial -mc 1 0 0 -o
freesurfer/lh.pial -mc 1 0 0    -w 1
freesurfer/lh.pial -mc 1 0 0    -w 5
freesurfer/lh.pial -mc 1 0 0    -w 10
freesurfer/lh.pial -mc 1 0 0 -o -w 1
freesurfer/lh.pial -mc 1 0 0 -o -w 5
freesurfer/lh.pial -mc 1 0 0 -o -w 10
freesurfer/lh.pial -mc 1 0 0 -o -w 10 -cm hot -vd freesurfer/lh.curv
freesurfer/lh.pial -mc 1 0 0 -o -w 10 -cm hot -vd freesurfer/lh.curv

{{asmgh('3d.nii.gz')}} freesurfer/lh.pial -r 3d.mgh -s torig
{{asmgh('3d.nii.gz')}} freesurfer/lh.pial -r 3d.mgh -s affine
{{asmgh('3d.nii.gz')}} freesurfer/lh.pial -r 3d.mgh -s pixdim
{{asmgh('3d.nii.gz')}} freesurfer/lh.pial -r 3d.mgh -s id
"""

def asmgh(infile):
    outfile = op.basename(fslimage.removeExt(infile))
    outfile = outfile + '.mgh'
    inimg   = fslimage.Image(infile)
    outimg  = nib.MGHImage(inimg.data, inimg.voxToWorldMat)
    outimg.to_filename(outfile)
    return outfile


def test_overlay_freesurfermesh():
    extras = {'asmgh' : asmgh}
    run_cli_tests('test_overlay_freesurfermesh',
                  cli_tests,
                  extras=extras,
                  threshold=25)
