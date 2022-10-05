"""Provide a scene editor class for the novelyst plugin.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/novelyst_editor
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import webbrowser
import tkinter as tk
from tkinter import messagebox
from nveditorlib.nv_editor_globals import *
from nveditorlib.text_box import TextBox

HELP_URL = 'https://peter88213.github.io/novelyst_editor/usage'
KEY_QUIT_PROGRAM = ('<Control-q>', 'Ctrl-Q')
KEY_APPLY_CHANGES = ('<Control-s>', 'Ctrl-S')
KEY_UPDATE_WORDCOUNT = ('<F5>', 'F5')
KEY_SPLIT_SCENE = ('<Control-Alt-s>', 'Ctrl-Alt-S')
KEY_ITALIC = ('<Control-i>', 'Ctrl-I')
KEY_BOLD = ('<Control-b>', 'Ctrl-B')
KEY_PLAIN = ('<Control-m>', 'Ctrl-M')


class SceneEditor(tk.Toplevel):
    """A separate scene editor window with a menu bar, a text box, and a status bar."""

    def __init__(self, ui, scId, size, icon=None):
        self._ui = ui
        self._scene = self._ui.ywPrj.scenes[scId]
        self._scId = scId

        # Create an independent editor window.
        super().__init__()
        self.title(f'{self._scene.title} - {self._ui.ywPrj.title}, {_("Scene")} ID {scId}')
        self.geometry(size)
        if icon:
            self.iconphoto(False, icon)

        # Add a main menu bar to the editor window.
        self._mainMenu = tk.Menu(self)
        self.config(menu=self._mainMenu)

        '''
        # Add a button bar to the editor window.
        self._buttonBar = tk.Frame(self)
        self._buttonBar.pack(expand=False, fill=tk.BOTH)
        '''

        # Add a text editor with scrollbar to the editor window.
        self._sceneEditor = TextBox(self, wrap='word', undo=True, autoseparators=True, spacing1=15, spacing2=5, maxundo=-1, height=25, width=60, padx=5, pady=5)
        self._sceneEditor.pack(expand=True, fill=tk.BOTH)
        self._sceneEditor.pack_propagate(0)

        # Add a status bar to the editor window.
        self._statusBar = tk.Label(self, text='', anchor='w', padx=5, pady=2)
        self._statusBar.pack(expand=False, fill=tk.BOTH)

        # Load the scene content into the text editor.
        if self._ui.ywPrj.scenes[scId].sceneContent:
            self._sceneEditor.set_text(self._scene.sceneContent)
        self._initialWc = self._sceneEditor.count_words()
        self.show_wordcount()

        #--- Configure the user interface.

        '''
        # Add buttons to the button bar.
        tk.Button(self._buttonBar, text=_('Copy'), command=lambda: self._sceneEditor.event_generate("<<Copy>>")).pack(side=tk.LEFT)
        tk.Button(self._buttonBar, text=_('Cut'), command=lambda: self._sceneEditor.event_generate("<<Cut>>")).pack(side=tk.LEFT)
        tk.Button(self._buttonBar, text=_('Paste'), command=lambda: self._sceneEditor.event_generate("<<Paste>>")).pack(side=tk.LEFT)
        tk.Button(self._buttonBar, text=_('Italic'), command=self._sceneEditor.italic).pack(side=tk.LEFT)
        tk.Button(self._buttonBar, text=_('Bold'), command=self._sceneEditor.bold).pack(side=tk.LEFT)
        '''

        # Add a "File" Submenu to the editor window.
        self._fileMenu = tk.Menu(self._mainMenu, tearoff=0)
        self._mainMenu.add_cascade(label=_('File'), menu=self._fileMenu)
        self._fileMenu.add_command(label=_('Apply changes'), accelerator=KEY_APPLY_CHANGES[1], command=self._apply_changes)
        self._fileMenu.add_command(label=_('Exit'), accelerator=KEY_QUIT_PROGRAM[1], command=self.on_quit)

        # Add an "Edit" Submenu to the editor window.
        self._editMenu = tk.Menu(self._mainMenu, tearoff=0)
        self._mainMenu.add_cascade(label=_('Edit'), menu=self._editMenu)
        self._editMenu.add_command(label=_('Copy'), accelerator='Ctrl-C', command=lambda: self._sceneEditor.event_generate("<<Copy>>"))
        self._editMenu.add_command(label=_('Cut'), accelerator='Ctrl-X', command=lambda: self._sceneEditor.event_generate("<<Cut>>"))
        self._editMenu.add_command(label=_('Paste'), accelerator='Ctrl-V', command=lambda: self._sceneEditor.event_generate("<<Paste>>"))
        self._editMenu.add_separator()
        self._editMenu.add_command(label=_('Split at cursor position'), accelerator=KEY_SPLIT_SCENE[1], command=self._split_scene)

        # Add a "Format" Submenu to the editor window.
        self._formatMenu = tk.Menu(self._mainMenu, tearoff=0)
        self._mainMenu.add_cascade(label=_('Format'), menu=self._formatMenu)
        self._formatMenu.add_command(label=_('Italic'), accelerator=KEY_ITALIC[1], command=self._sceneEditor.italic)
        self._formatMenu.add_command(label=_('Bold'), accelerator=KEY_BOLD[1], command=self._sceneEditor.bold)
        self._formatMenu.add_command(label=_('Plain'), accelerator=KEY_PLAIN[1], command=self._sceneEditor.plain)

        # Add a "Word count" Submenu to the editor window.
        self._wcMenu = tk.Menu(self._mainMenu, tearoff=0)
        self._mainMenu.add_cascade(label=_('Word count'), menu=self._wcMenu)
        self._wcMenu.add_command(label=_('Update'), accelerator=KEY_UPDATE_WORDCOUNT[1], command=self.show_wordcount)
        self._wcMenu.add_command(label=_('Enable live update'), command=self._live_wc_on)
        self._wcMenu.add_command(label=_('Disable live update'), command=self._live_wc_off)

        # Help
        self.helpMenu = tk.Menu(self._mainMenu, tearoff=0)
        self._mainMenu.add_cascade(label=_('Help'), menu=self.helpMenu)
        self.helpMenu.add_command(label=_('Online help'), command=lambda: webbrowser.open(HELP_URL))

        # Event bindings.
        self.bind_class('Text', KEY_APPLY_CHANGES[0], self._apply_changes)
        self.bind_class('Text', KEY_QUIT_PROGRAM[0], self.on_quit)
        self.bind_class('Text', KEY_UPDATE_WORDCOUNT[0], self.show_wordcount)
        self.bind_class('Text', KEY_SPLIT_SCENE[0], self._split_scene)
        self.bind_class('Text', KEY_ITALIC[0], self._sceneEditor.italic)
        self.bind_class('Text', KEY_BOLD[0], self._sceneEditor.bold)
        self.bind_class('Text', KEY_PLAIN[0], self._sceneEditor.plain)
        self.protocol("WM_DELETE_WINDOW", self.on_quit)

        self.focus()
        self.isOpen = True
        self._wcMenu.entryconfig(_('Disable live update'), state='disabled')

    def _live_wc_on(self, event=None):
        self.bind('<KeyRelease>', self.show_wordcount)
        self._wcMenu.entryconfig(_('Enable live update'), state='disabled')
        self._wcMenu.entryconfig(_('Disable live update'), state='normal')
        self.show_wordcount()

    def _live_wc_off(self, event=None):
        self.unbind('<KeyRelease>')
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
        self.destroy()
        self.isOpen = False

    def lift(self):
        """Bring window to the foreground and give it the focus.
        
        Extends the superclass method.
        """
        super().lift()
        self.focus()

    def _split_scene(self, event=None):
        """Split a scene at the cursor position."""
        if not self._ui.ask_yes_no(f'{_("Move the text from the cursor position to the end into a new scene")}?'):
            return

        # Add a new scene.
        thisNode = f'{self._ui.tv.SCENE_PREFIX}{self._scId}'
        newId = self._ui.tv.add_scene(selection=thisNode)
        if newId:
            # Cut the actual scene's content from the cursor position to the end.
            newContent = self._sceneEditor.get_text(tk.INSERT, tk.END).strip(' \n')
            self._sceneEditor.delete(tk.INSERT, tk.END)
            self._apply_changes()

            # Copy the scene content to the new scene.
            self._ui.ywPrj.scenes[newId].sceneContent = newContent

            # Append the new scene to the previous scene.
            self._ui.ywPrj.scenes[newId].appendToPrev = True

            # Copy the scene status.
            status = self._ui.ywPrj.scenes[self._scId].status
            self._ui.ywPrj.scenes[newId].status = status

            # Copy the scene type.
            scType = self._ui.ywPrj.scenes[self._scId].scType
            self._ui.ywPrj.scenes[newId].scType = scType

            # Copy the viewpoint character.
            if self._ui.ywPrj.scenes[self._scId].characters:
                viewpoint = self._ui.ywPrj.scenes[self._scId].characters[0]
                self._ui.ywPrj.scenes[newId].characters = [viewpoint]

