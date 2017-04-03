"""A graphical user interface for chord_generator.py."""

import sys
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
import wx
from wx.lib.sized_controls import SizedFrame
from chords import parser, main

parser.error = print


def error(message, **kwargs):
    """Popup an error message."""
    kwargs.setdefault('style', wx.ICON_EXCLAMATION)
    return wx.MessageBox(str(message), kwargs.pop('title', 'Error'), **kwargs)


class AddFrame(SizedFrame):
    """Add markings with this frame."""

    def __init__(self, parent):
        """Pass the parent which has an add_marking method."""
        self.parent = parent
        super(AddFrame, self).__init__(parent, title='Add A Marking')
        p = self.GetContentsPane()
        for entry in [
            'string',
            'fret',
            'finger'
        ]:
            wx.StaticText(p, label='&{}'.format(entry.title()))
            setattr(
                self,
                entry,
                wx.TextCtrl(p)
            )
        self.ok_btn = wx.Button(p, label='&OK')
        self.ok_btn.Bind(wx.EVT_BUTTON, self.on_ok)
        self.ok_btn.SetDefault()
        wx.Button(p, label='&Cancel').Bind(
            wx.EVT_BUTTON,
            lambda event: self.Close(True)
        )
        self.Show(True)
        self.Maximize()

    def on_ok(self, event):
        """OK button was pressed."""
        string = self.string.GetValue()
        fret = self.fret.GetValue()
        finger = self.finger.GetValue()
        if not string:
            self.string.SetFocus()
            return error('You must specify a string.')
        if not fret:
            if finger:
                self.fret.SetFocus()
                return error('You cannot have a finger with an empty fret.')
        res = string
        if fret:
            res += '.{}'.format(fret)
        if finger:
            res += '.{}'.format(finger)
        self.parent.add_marking(res)
        self.Close(True)


class ChordsFrame(wx.Frame):
    """The frame for showing chords."""
    def __init__(self):
        self._markings = []
        super(ChordsFrame, self).__init__(None, title='Chord Generator')
        p = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer.Add(wx.StaticText(p, label='&Markings'), 0, wx.GROW)
        self.markings = wx.ListBox(p)
        top_sizer.Add(self.markings, 1, wx.GROW)
        self.add_btn = wx.Button(p, label='&Add')
        button_sizer.Add(self.add_btn, 1, wx.GROW)
        self.add_btn.Bind(wx.EVT_BUTTON, lambda event: AddFrame(self))
        self.generate_btn = wx.Button(p, label='&Generate')
        button_sizer.Add(self.generate_btn, 0, wx.GROW)
        self.generate_btn.Bind(wx.EVT_BUTTON, self.on_generate)
        self.preferences_btn = wx.Button(p, label='&Preferences')
        button_sizer.Add(self.preferences_btn, 1, wx.GROW)
        self.preferences_btn.Bind(wx.EVT_BUTTON, self.on_preferences)
        self.save_btn = wx.Button(p, label='&Save')
        button_sizer.Add(self.save_btn, 0, wx.GROW)
        self.save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        top_sizer.Add(button_sizer, 0, wx.GROW)
        main_sizer.Add(top_sizer, 1, wx.GROW)
        main_sizer.Add(wx.StaticText(p, label='&Output'), 0, wx.GROW)
        self.output = wx.TextCtrl(
            p,
            style=wx.TE_MULTILINE | wx.TE_RICH | wx.TE_DONTWRAP
        )
        main_sizer.Add(self.output, 1, wx.GROW)

    def add_marking(self, marking):
        s = marking.split('.')
        if len(s) == 1:
            res = 'Don\'t play string %s.' % s[0]
        else:
            res = 'String {}, fret {}, '.format(s[0], s[1])
            if len(s) == 2:
                res += 'any finger'
            else:
                res += 'finger {}'.format(s[2])
        res += '.'
        self._markings.append(marking)
        self.markings.Append(res)

    def on_generate(self, event):
        """Generate button was pressed."""
        sys.argv = [
            sys.argv[0],
            *self._markings
        ]
        buf = StringIO()
        with redirect_stderr(buf), redirect_stdout(buf):
            main()
        buf.seek(0)
        self.output.SetValue(buf.read())
        self.output.SetFocus()

    def on_preferences(self, event):
        """Preferences button was clicked."""
        error('Preferences.')

    def on_save(self, event):
        """Save button was pressed."""
        error('Save button was pressed.')


if __name__ == '__main__':
    app = wx.App()
    frame = ChordsFrame()
    frame.Show(True)
    frame.Maximize()
    app.MainLoop()
