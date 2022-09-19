"""A multi-scene editor plugin for novelyst.

Compatibility: novelyst v0.14.1 API 
Requires Python 3.6+
Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/novelyst_editor
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import re
import sys
import tkinter as tk
import locale
import gettext
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import messagebox

# Initialize localization.
LOCALE_PATH = f'{os.path.dirname(sys.argv[0])}/locale/'
CURRENT_LANGUAGE = locale.getdefaultlocale()[0][:2]
try:
    t = gettext.translation('novelyst_editor', LOCALE_PATH, languages=[CURRENT_LANGUAGE])
    _ = t.gettext
except:

    def _(message):
        return message

APPLICATION = _('Scene Editor')
PLUGIN = f'{APPLICATION} plugin v@release'
ICON = 'sLogo32'

KEY_QUIT_PROGRAM = ('<Control-q>', 'Ctrl-Q')
KEY_APPLY_CHANGES = ('<Control-s>', 'Ctrl-S')
KEY_UPDATE_WORDCOUNT = ('<F5>', 'F5')


class Plugin:
    """novelyst multi-scene editor plugin class.
    
    Public methods:
        on_quit() -- apply changes before closing the editor windows.       
    """

    def __init__(self, ui):
        """Add a submenu to the main menu.
        
        Positional arguments:
            ui -- reference to the NovelystTk instance of the application.
        """
        self._ui = ui

        # Add the "Edit" command to novelyst's "Scene" menu.
        self._ui.sceneMenu.add_separator()
        self._ui.sceneMenu.add_command(label=_('Edit'), underline=0, command=self._edit_scene)
        self._ui.tv.tree.bind('<Double-1>', self._edit_scene)
        self.sceneEditors = {}
        try:
            path = os.path.dirname(sys.argv[0])
            if not path:
                path = '.'
            self._icon = tk.PhotoImage(file=f'{path}/icons/{ICON}.png')
        except:
            self._icon = None

    def _edit_scene(self, event=None):
        """Create a scene editor window with a menu bar, a text box, and a status bar."""
        if self._ui.isLocked:
            messagebox.showinfo(PLUGIN, _('Cannot edit scenes, because the project is locked.'))
            return

        try:
            nodeId = self._ui.tv.tree.selection()[0]
            if nodeId.startswith(self._ui.tv.SCENE_PREFIX):
                # A scene is selected
                scId = nodeId[2:]
                if scId in self.sceneEditors and self.sceneEditors[scId].isOpen:
                    self.sceneEditors[scId].lift()
                    return

                self.sceneEditors[scId] = SceneEditor(self._ui, scId, icon=self._icon)
        except IndexError:
            # Nothing selected
            pass

    def on_quit(self, event=None):
        """Close all open scene editor windows."""
        for scId in self.sceneEditors:
            if self.sceneEditors[scId].isOpen:
                self.sceneEditors[scId].on_quit()


class SceneEditor:
    """A separate scene editor window with a menu bar, a text box, and a status bar."""

    def __init__(self, ui, scId, icon=None):
        self._ui = ui
        self._scene = self._ui.ywPrj.scenes[scId]

        # Create an independent editor window.
        self._editWindow = tk.Toplevel()
        self._editWindow.title(f'{self._scene.title} - {self._ui.ywPrj.title}, {_("Scene")} ID {scId}')
        if icon:
            self._editWindow.iconphoto(False, icon)

        # Add a main menu bar to the editor window.
        self._mainMenu = tk.Menu(self._editWindow)

        # Add a "File" Submenu to the editor window.
        self._fileMenu = tk.Menu(self._mainMenu, tearoff=0)
        self._mainMenu.add_cascade(label=_('File'), menu=self._fileMenu)
        self._fileMenu.add_command(label=_('Apply changes'), accelerator=KEY_APPLY_CHANGES[1], command=self._apply_changes)
        self._fileMenu.add_command(label=_('Exit'), accelerator=KEY_QUIT_PROGRAM[1], command=self.on_quit)
        self._editWindow.config(menu=self._mainMenu)

        # Add a "Word count" Submenu to the editor window.
        self._wcMenu = tk.Menu(self._mainMenu, tearoff=0)
        self._mainMenu.add_cascade(label=_('Word count'), menu=self._wcMenu)
        self._wcMenu.add_command(label=_('Update'), accelerator=KEY_UPDATE_WORDCOUNT[1], command=self.show_wordcount)
        self._wcMenu.add_command(label=_('Enable live update'), command=self._live_wc_on)
        self._wcMenu.add_command(label=_('Disable live update'), command=self._live_wc_off)

        # Add a text editor with scrollbar to the editor window.
        self._sceneEditor = TextBox(self._editWindow, wrap='word', undo=True, autoseparators=True, spacing1=15, spacing2=5, maxundo=-1, height=25, width=60, padx=5, pady=5)
        self._sceneEditor.pack(expand=True, fill=tk.BOTH)

        # Add a status bar to the editor window.
        self._statusBar = tk.Label(self._editWindow, text='', anchor='w', padx=5, pady=2)
        self._statusBar.pack(expand=False, fill='both')

        # Load the scene content into the text editor.
        if self._ui.ywPrj.scenes[scId].sceneContent:
            self._sceneEditor.set_text(self._scene.sceneContent)
        self._initialWc = self._sceneEditor.count_words()
        self.show_wordcount()

        # Event bindings.
        self._editWindow.bind(KEY_APPLY_CHANGES[0], self._apply_changes)
        self._editWindow.bind(KEY_QUIT_PROGRAM[0], self.on_quit)
        self._editWindow.bind(KEY_UPDATE_WORDCOUNT[0], self.show_wordcount)
        self._editWindow.protocol("WM_DELETE_WINDOW", self.on_quit)

        self._editWindow.focus()
        self.isOpen = True
        self._wcMenu.entryconfig(_('Disable live update'), state='disabled')

    def _live_wc_on(self, event=None):
        self._editWindow.bind('<KeyRelease>', self.show_wordcount)
        self._wcMenu.entryconfig(_('Enable live update'), state='disabled')
        self._wcMenu.entryconfig(_('Disable live update'), state='normal')
        self.show_wordcount()

    def _live_wc_off(self, event=None):
        self._editWindow.unbind('<KeyRelease>')
        self._wcMenu.entryconfig(_('Enable live update'), state='normal')
        self._wcMenu.entryconfig(_('Disable live update'), state='disabled')

    def show_status(self, message=None):
        """Display a message on the status bar."""
        self._statusBar.config(text=message)

    def show_wordcount(self, event=None):
        """Display a message on the status bar."""
        wc = self._sceneEditor.count_words()
        diff = wc - self._initialWc
        self._statusBar.config(text=f'{wc} {_("words")} ({diff} {_("new")})')

    def _apply_changes(self, event=None):
        """Write the editor content to the project, if possible."""
        sceneText = self._sceneEditor.get_text()
        if sceneText or self._scene.sceneContent:
            if self._scene.sceneContent != sceneText:
                if self._ui.isLocked:
                    messagebox.showinfo(PLUGIN, _('Cannot apply scene changes, because the project is locked.'))
                    return

                self._scene.sceneContent = sceneText
                self._ui.isModified = True

    def on_quit(self, event=None):
        """Exit the editor. Apply changes, if possible."""
        sceneText = self._sceneEditor.get_text()
        if sceneText or self._scene.sceneContent:
            if self._scene.sceneContent != sceneText:
                if self._ui.ask_yes_no(_('Apply scene changes?')):
                    if self._ui.isLocked:
                        if self._ui.ask_yes_no(_('Cannot apply scene changes, because the project is locked.\nUnlock and apply changes?')):
                            self._ui.unlock()
                            self._scene.sceneContent = sceneText
                            self._ui.isModified = True
                    else:
                        self._scene.sceneContent = sceneText
                        self._ui.isModified = True
        self._editWindow.destroy()
        self.isOpen = False

    def lift(self):
        """Bring window to the foreground and give it the focus."""
        self._editWindow.lift()
        self._editWindow.focus()


class TextBox(scrolledtext.ScrolledText):
    """If a more sophisticated text box is needed, create it here."""

    def get_text(self):
        text = self.get('1.0', tk.END).strip(' \n')
        # convert text to yWriter markup, if applicable.
        return text

    def set_text(self, text):
        # convert text from yWriter markup, if applicable.
        self.insert(tk.END, text)
        self.edit_reset()
        # this is to prevent the user from clearing the box with Ctrl-Z

    def count_words(self):
        text = re.sub('--|—|–|…', ' ', self.get('1.0', tk.END))
        # Make dashes separate words
        text = re.sub('\[.+?\]|\/\*.+?\*\/|\.|\,|-', '', text)
        # Remove comments and yWriter raw markup for word count; make hyphens join words
        wordList = text.split()
        return len(wordList)
