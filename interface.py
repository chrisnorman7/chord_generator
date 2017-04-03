"""A graphical user interface for chord_generator.py."""

import sys
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
from argparse import _StoreAction, _StoreTrueAction, _StoreFalseAction
import wx
from wx.lib.sized_controls import SizedFrame
from chords import arguments, main


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
        p.SetSizerType('form')
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


class ChordsFrame(SizedFrame):
    """The frame for showing chords."""
    def __init__(self):
        self._markings = []
        super(ChordsFrame, self).__init__(None, title='Chord Generator')
        p = self.GetContentsPane()
        p.SetSizerType('form')
        self.advanced_controls = {}
        for a in arguments:
            wx.StaticText(p, label=a.help)
            if isinstance(a, _StoreAction):
                ctrl = wx.TextCtrl(p, style=wx.TE_RICH)
            elif isinstance(a, (_StoreTrueAction, _StoreFalseAction)):
                ctrl = wx.CheckBox(p, label=a.help)
            else:
                error('No clue how to handle: %s.' % a.help)
                continue
            self.advanced_controls[a] = ctrl
        self.on_restore(None)
        wx.StaticText(p, label='&Markings')
        self.markings = wx.ListBox(p)
        wx.Button(p, label='&Add').Bind(
            wx.EVT_BUTTON,
            lambda event:
            AddFrame(self)
        )
        wx.Button(p, label='&Delete').Bind(wx.EVT_BUTTON, self.on_delete)
        wx.Button(p, label='&Generate').Bind(wx.EVT_BUTTON, self.on_generate)
        wx.Button(p, label='&Preferences').Bind(
            wx.EVT_BUTTON,
            self.on_preferences
        )
        wx.Button(p, label='&Save').Bind(wx.EVT_BUTTON, self.on_save)
        wx.Button(p, label='&Restore Advanced Defaults').Bind(
            wx.EVT_BUTTON,
            self.on_restore
        )
        wx.StaticText(p, label='&Output')
        self.output = wx.TextCtrl(
            p,
            style=wx.TE_MULTILINE | wx.TE_RICH | wx.TE_DONTWRAP
        )

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

    def on_delete(self, event):
        """Delete a marking."""
        cr = self.markings.GetSelection()
        if cr == -1:
            wx.Bell()
        else:
            self.markings.Delete(cr)
            del self._markings[cr]

    def on_generate(self, event):
        """Generate button was pressed."""
        event.Skip()
        s = StringIO()
        sys.argv = [sys.argv[0]]
        for argument, control in self.advanced_controls.items():
            name = argument.option_strings[-1]
            if isinstance(argument, _StoreTrueAction):
                if control.GetValue():
                    sys.argv.append(name)
            elif isinstance(argument, _StoreFalseAction):
                if not control.GetValue():
                    sys.argv.append(name)
            elif isinstance(argument, _StoreAction):
                sys.argv += [
                    name,
                    control.GetValue()
                ]
            else:
                error('No clue what to do with argument: %s.' % argument.help)
        sys.argv += self._markings
        with redirect_stdout(s), redirect_stderr(s):
            main()
        s.seek(0)
        self.output.SetValue(s.read())
        self.output.SetFocus()

    def on_preferences(self, event):
        """Preferences button was clicked."""
        error('Preferences.')

    def on_save(self, event):
        """Save button was pressed."""
        error('Save button was pressed.')

    def on_restore(self, event):
        """Restore all advanced settings to their defaults."""
        for argument, control in self.advanced_controls.items():
            try:
                if isinstance(argument, _StoreAction):
                    value = str(argument.default)
                else:
                    value = argument.default
                control.SetValue(value)
            except Exception as e:
                error(
                    'Failed to set the value for argument {}: {}.'.format(
                        argument.help,
                        e
                    )
                )


if __name__ == '__main__':
    app = wx.App()
    frame = ChordsFrame()
    frame.Show(True)
    frame.Maximize()
    app.MainLoop()
