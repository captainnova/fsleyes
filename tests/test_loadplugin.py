#!/usr/bin/env python
#
# test_loadplugin.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import os.path as op
import contextlib

import wx

try:
    from unittest import mock
except ImportError:
    import mock

import fsl.utils.tempdir          as tempdir
import fsl.utils.settings         as fslsettings
import fsleyes.actions.loadplugin as loadplugin
import fsleyes.plugins            as plugins


code = """
import fsleyes.views.viewpanel as vp

class MyViewPanel(vp.ViewPanel):
    pass
""".strip()


def test_LoadPluginAction():

    act = loadplugin.LoadPluginAction(None, None, None)

    class FileDialog(object):
        ShowModal_return = wx.ID_OK
        GetPath_return   = ''
        def __init__(self, *args, **kwargs):
            pass
        def ShowModal(self):
            return FileDialog.ShowModal_return
        def GetPath(self):
            return FileDialog.GetPath_return

    class MessageDialog(object):
        ShowModal_return = wx.ID_OK
        def __init__(self, *args, **kwargs):
            pass
        def ShowModal(self):
            return MessageDialog.ShowModal_return

    @contextlib.contextmanager
    def reportIfError(*a, **kwa):
        try:
            yield
        except Exception:
            pass

    with mock.patch('wx.FileDialog',    FileDialog), \
         mock.patch('wx.MessageDialog', MessageDialog), \
         mock.patch('fsleyes_widgets.utils.status.reportIfError',
                    reportIfError):
        FileDialog.ShowModal_return = wx.ID_CANCEL
        act()

        FileDialog.ShowModal_return = wx.ID_OK
        FileDialog.GetPath_return   = 'bad path'
        MessageDialog.ShowModal_return = wx.ID_CANCEL
        act()

        FileDialog.ShowModal_return = wx.ID_OK
        FileDialog.GetPath_return   = 'bad path'
        MessageDialog.ShowModal_return = wx.ID_NO
        act()

        FileDialog.ShowModal_return = wx.ID_OK
        FileDialog.GetPath_return   = 'bad path'
        MessageDialog.ShowModal_return = wx.ID_YES
        act()

        FileDialog.ShowModal_return = wx.ID_OK
        FileDialog.GetPath_return   = 'bad path'
        MessageDialog.ShowModal_return = wx.ID_YES
        act()

        with tempdir.tempdir(changeto=False) as td, \
             fslsettings.use(fslsettings.Settings(cfgdir=td)):
            with open(op.join(td, 'test_loadplugin.py'), 'wt') as f:
                f.write(code)

            FileDialog.GetPath_return = op.join(td, 'test_loadplugin.py')
            act()

            assert 'fsleyes-plugin-test-loadplugin' in plugins.listPlugins()
