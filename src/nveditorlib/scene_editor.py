"""Provide a scene editor class for the novelyst plugin.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/novelyst_editor
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import webbrowser
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from nveditorlib.nv_editor_globals import *
from nveditorlib.text_box import TextBox

HELP_URL = 'https://peter88213.github.io/novelyst_editor/usage'
KEY_QUIT_PROGRAM = ('<Control-q>', 'Ctrl-Q')
KEY_APPLY_CHANGES = ('<Control-s>', 'Ctrl-S')
KEY_UPDATE_WORDCOUNT = ('<F5>', 'F5')
KEY_SPLIT_SCENE = ('<Control-Alt-s>', 'Ctrl-Alt-S')
KEY_CREATE_SCENE = ('<Control-Alt-n>', 'Ctrl-Alt-N')
KEY_ITALIC = ('<Control-i>', 'Ctrl-I')
KEY_BOLD = ('<Control-b>', 'Ctrl-B')
KEY_PLAIN = ('<Control-m>', 'Ctrl-M')

COLOR_MODES = [
        (_('Bright mode'), 'black', 'white'),
        (_('Light mode'), 'black', 'antique white'),
        (_('Dark mode'), 'light grey', 'gray20'),
        ]
# (name, foreground, background) tuples for color modes.


class SceneEditor(tk.Toplevel):
    """A separate scene editor window with a menu bar, a text box, and a status bar.
    
    Public instance methods:
        lift() -- Bring window to the foreground and set the focus to the editor box.
        on_quit() -- Exit the editor. Apply changes, if possible.
        show_status(message=None) -- Display a message on the status bar.
        show_wordcount()-- Display the word count on the status bar.
    """
    liveWordCount = False
    colorMode = 0

    def __init__(self, plugin, ui, scId, size, icon=None):
        self._ui = ui
        self._plugin = plugin
        self._scene = self._ui.novel.scenes[scId]
        self._scId = scId

        # Create an independent editor window.
        super().__init__()
        self.geometry(size)
        if icon:
            self.iconphoto(False, icon)

        # Add a main menu bar to the editor window.
        self._mainMenu = tk.Menu(self)
        self.config(menu=self._mainMenu)

        '''
        # Add a button bar to the editor window.
        self._buttonBar = tk.Frame(self)
        self._buttonBar.pack(expand=False, fill='both')
        '''

        # Add a text editor with scrollbar to the editor window.
        self._sceneEditor = TextBox(self,
                                    wrap='word',
                                    undo=True,
                                    autoseparators=True,
                                    spacing1=self._plugin.kwargs['paragraph_spacing'],
                                    spacing2=self._plugin.kwargs['line_spacing'],
                                    maxundo=-1,
                                    padx=self._plugin.kwargs['margin_x'],
                                    pady=self._plugin.kwargs['margin_y'],
                                    font=(self._plugin.kwargs['font_family'], self._plugin.kwargs['font_size']),
                                    )
        self._sceneEditor.pack(expand=True, fill='both')
        self._sceneEditor.pack_propagate(0)
        self._set_editor_colors()

        # Add a status bar to the editor window.
        self._statusBar = tk.Label(self, text='', anchor='w', padx=5, pady=2)
        self._statusBar.pack(expand=False, side='left')

        # Add buttons to the bottom line.
        ttk.Button(self, text=_('Next'), command=self._load_next).pack(side='right')
        ttk.Button(self, text=_('Exit'), command=self.on_quit).pack(side='right')
        ttk.Button(self, text=_('Previous'), command=self._load_prev).pack(side='right')

        # Load the scene content into the text editor.
        self._load_scene()

        #--- Configure the user interface.
        '''
        # Add buttons to the button bar.
        tk.Button(self._buttonBar, text=_('Copy'), command=lambda: self._sceneEditor.event_generate("<<Copy>>")).pack(side='left')
        tk.Button(self._buttonBar, text=_('Cut'), command=lambda: self._sceneEditor.event_generate("<<Cut>>")).pack(side='left')
        tk.Button(self._buttonBar, text=_('Paste'), command=lambda: self._sceneEditor.event_generate("<<Paste>>")).pack(side='left')
        tk.Button(self._buttonBar, text=_('Italic'), command=self._sceneEditor.italic).pack(side='left')
        tk.Button(self._buttonBar, text=_('Bold'), command=self._sceneEditor.bold).pack(side='left')
        '''

        # Add a "File" Submenu to the editor window.
        self._fileMenu = tk.Menu(self._mainMenu, tearoff=0)
        self._mainMenu.add_cascade(label=_('Scene'), menu=self._fileMenu)
        self._fileMenu.add_command(label=_('Next'), command=self._load_next)
        self._fileMenu.add_command(label=_('Previous'), command=self._load_prev)
        self._fileMenu.add_command(label=_('Apply changes'), accelerator=KEY_APPLY_CHANGES[1], command=self._apply_changes)
        self._fileMenu.add_command(label=_('Exit'), accelerator=KEY_QUIT_PROGRAM[1], command=self.on_quit)

        # Add a "View" Submenu to the editor window.
        self._viewMenu = tk.Menu(self._mainMenu, tearoff=0)
        self._mainMenu.add_cascade(label=_('View'), menu=self._viewMenu)
        self._viewMenu.add_command(label=COLOR_MODES[0][0], command=lambda: self._set_view_mode(mode=0))
        self._viewMenu.add_command(label=COLOR_MODES[1][0], command=lambda: self._set_view_mode(mode=1))
        self._viewMenu.add_command(label=COLOR_MODES[2][0], command=lambda: self._set_view_mode(mode=2))
        # note: this can't be done with a loop because of the "lambda" evaluation at runtime

        # Add an "Edit" Submenu to the editor window.
        self._editMenu = tk.Menu(self._mainMenu, tearoff=0)
        self._mainMenu.add_cascade(label=_('Edit'), menu=self._editMenu)
        self._editMenu.add_command(label=_('Copy'), accelerator='Ctrl-C', command=lambda: self._sceneEditor.event_generate("<<Copy>>"))
        self._editMenu.add_command(label=_('Cut'), accelerator='Ctrl-X', command=lambda: self._sceneEditor.event_generate("<<Cut>>"))
        self._editMenu.add_command(label=_('Paste'), accelerator='Ctrl-V', command=lambda: self._sceneEditor.event_generate("<<Paste>>"))
        self._editMenu.add_separator()
        self._editMenu.add_command(label=_('Split at cursor position'), accelerator=KEY_SPLIT_SCENE[1], command=self._split_scene)
        self._editMenu.add_command(label=_('Create scene'), accelerator=KEY_CREATE_SCENE[1], command=self._create_scene)

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
        self.bind_class('Text', KEY_CREATE_SCENE[0], self._create_scene)
        self.bind_class('Text', KEY_ITALIC[0], self._sceneEditor.italic)
        self.bind_class('Text', KEY_BOLD[0], self._sceneEditor.bold)
        self.bind_class('Text', KEY_PLAIN[0], self._sceneEditor.plain)
        self.protocol("WM_DELETE_WINDOW", self.on_quit)

        if SceneEditor.liveWordCount:
            self._live_wc_on()
        else:
            self._wcMenu.entryconfig(_('Disable live update'), state='disabled')

        self.lift()
        self.isOpen = True

    def lift(self):
        """Bring window to the foreground and set the focus to the editor box.
        
        Extends the superclass method.
        """
        super().lift()
        self._sceneEditor.focus()

    def on_quit(self, event=None):
        """Exit the editor. Apply changes, if possible."""
        self._apply_changes_after_asking()
        self._plugin.kwargs['window_geometry'] = self.winfo_geometry()
        self.destroy()
        self.isOpen = False

    def show_status(self, message=None):
        """Display a message on the status bar."""
        self._statusBar.config(text=message)

    def show_wordcount(self, event=None):
        """Display the word count on the status bar."""
        wc = self._sceneEditor.count_words()
        diff = wc - self._initialWc
        self._statusBar.config(text=f'{wc} {_("words")} ({diff} {_("new")})')

    def _create_scene(self, event=None):
        """Create a new scene after the currently edited scene."""
        if self._ui.isLocked:
            messagebox.showinfo(APPLICATION, _('Cannot create scenes, because the project is locked.'), parent=self)
            self.lift()
            return

        self.lift()
        # Add a scene after the currently edited scene.
        thisNode = f'{self._ui.tv.SCENE_PREFIX}{self._scId}'
        newId = self._ui.tv.add_scene(selection=thisNode,
                                      scType=self._ui.novel.scenes[self._scId].scType,
                                      )
        # Go to the new scene.
        self._load_next()

    def _apply_changes(self, event=None):
        """Transfer the editor content to the project, if modified."""
        sceneText = self._sceneEditor.get_text()
        if sceneText or self._scene.sceneContent:
            if self._scene.sceneContent != sceneText:
                self._transfer_text(sceneText)

    def _apply_changes_after_asking(self, event=None):
        """Transfer the editor content to the project, if modified. Ask first."""
        sceneText = self._sceneEditor.get_text()
        if sceneText or self._scene.sceneContent:
            if self._scene.sceneContent != sceneText:
                if messagebox.askyesno(APPLICATION, _('Apply scene changes?'), parent=self):
                    self._transfer_text(sceneText)

    def _live_wc_off(self, event=None):
        self.unbind('<KeyRelease>')
        self._wcMenu.entryconfig(_('Enable live update'), state='normal')
        self._wcMenu.entryconfig(_('Disable live update'), state='disabled')
        SceneEditor.liveWordCount = False

    def _live_wc_on(self, event=None):
        self.bind('<KeyRelease>', self.show_wordcount)
        self._wcMenu.entryconfig(_('Enable live update'), state='disabled')
        self._wcMenu.entryconfig(_('Disable live update'), state='normal')
        self.show_wordcount()
        SceneEditor.liveWordCount = True

    def _load_next(self, event=None):
        """Load the next scene in the tree."""
        self._apply_changes_after_asking()
        thisNode = f'{self._ui.tv.SCENE_PREFIX}{self._scId}'
        nextNode = self._ui.tv.next_node(thisNode, '')
        if nextNode:
            self._ui.tv.go_to_node(nextNode)
            scId = nextNode[2:]
            self._scId = scId
            self._scene = self._ui.novel.scenes[scId]
            self._sceneEditor.clear()
            self._load_scene()
        self.lift()

    def _load_prev(self, event=None):
        """Load the previous scene in the tree."""
        self._apply_changes_after_asking()
        thisNode = f'{self._ui.tv.SCENE_PREFIX}{self._scId}'
        prevNode = self._ui.tv.prev_node(thisNode, '')
        if prevNode:
            self._ui.tv.go_to_node(prevNode)
            scId = prevNode[2:]
            self._scId = scId
            self._scene = self._ui.novel.scenes[scId]
            self._sceneEditor.clear()
            self._load_scene()
        self.lift()

    def _load_scene(self):
        """Load the scene content into the text editor."""
        self.title(f'{self._scene.title} - {self._ui.novel.title}, {_("Scene")} ID {self._scId}')
        if self._scene.sceneContent:
            self._sceneEditor.set_text(self._scene.sceneContent)
        self._initialWc = self._sceneEditor.count_words()
        self.show_wordcount()

    def _set_editor_colors(self):
        self._sceneEditor['fg'] = COLOR_MODES[SceneEditor.colorMode][1]
        self._sceneEditor['bg'] = COLOR_MODES[SceneEditor.colorMode][2]
        self._sceneEditor['insertbackground'] = COLOR_MODES[SceneEditor.colorMode][1]

    def _set_view_mode(self, event=None, mode=0):
        SceneEditor.colorMode = mode
        self._set_editor_colors()

    def _split_scene(self, event=None):
        """Split a scene at the cursor position."""
        if self._ui.isLocked:
            messagebox.showinfo(APPLICATION, _('Cannot split the scene, because the project is locked.'), parent=self)
            self.lift()
            return

        if not messagebox.askyesno(APPLICATION, f'{_("Move the text from the cursor position to the end into a new scene")}?', parent=self):
            self.lift()
            return

        self.lift()
        # Add a new scene.
        thisNode = f'{self._ui.tv.SCENE_PREFIX}{self._scId}'
        newId = self._ui.tv.add_scene(selection=thisNode,
                                      appendToPrev=True,
                                      scType=self._ui.novel.scenes[self._scId].scType,
                                      status=self._ui.novel.scenes[self._scId].status
                                      )
        if newId:
            # Cut the actual scene's content from the cursor position to the end.
            newContent = self._sceneEditor.get_text('insert', 'end').strip(' \n')
            self._sceneEditor.delete('insert', 'end')
            self._apply_changes()

            # Copy the scene content to the new scene.
            self._ui.novel.scenes[newId].sceneContent = newContent

            # Copy the viewpoint character.
            if self._ui.novel.scenes[self._scId].characters:
                viewpoint = self._ui.novel.scenes[self._scId].characters[0]
                self._ui.novel.scenes[newId].characters = [viewpoint]

            # Go to the new scene.
            self._load_next()

    def _transfer_text(self, sceneText):
        """Transfer the changed editor content to the scene, if possible.
        
        On success, set the user interface's change flag. 
        """
        if self._ui.isLocked:
            if messagebox.askyesno(APPLICATION, _('Cannot apply scene changes, because the project is locked.\nUnlock and apply changes?'), parent=self):
                self._ui.unlock()
                self._scene.sceneContent = sceneText
                self._ui.isModified = True
            self.lift()
        else:
            self._scene.sceneContent = sceneText
            self._ui.isModified = True
        self._ui.show_status()

