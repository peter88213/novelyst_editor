"""A multi-scene "plain text" editor plugin for novelyst.

Requires Python 3.6+
Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/novelyst_editor
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import os
import sys
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from nveditorlib.nv_editor_globals import *
from nveditorlib.scene_editor import SceneEditor
from nveditorlib.configuration import Configuration

SETTINGS = dict(
        window_geometry='600x800',
        color_mode=0,
        color_fg_bright='white',
        color_bg_bright='black',
        color_fg_light='antique white',
        color_bg_light='black',
        color_fg_dark='light grey',
        color_bg_dark='gray20',
        font_family='Courier',
        font_size=12,
        line_spacing=6,
        paragraph_spacing=18,
        margin_x=40,
        margin_y=20,
        )
OPTIONS = dict(
        live_wordcount=False,
        )


class Plugin:
    """novelyst multi-scene "plain text" editor plugin class.
    
    Public methods:
        on_close() -- Actions to be performed when a project is closed.       
        on_quit() -- Actions to be performed when novelyst is closed.       
    """
    VERSION = '@release'
    NOVELYST_API = '4.0'
    DESCRIPTION = 'A multi-scene "plain text" editor'
    URL = 'https://peter88213.github.io/novelyst_editor'

    def install(self, ui):
        """Add a submenu to the main menu.
        
        Positional arguments:
            ui -- reference to the NovelystTk instance of the application.
        """
        self._ui = ui

        #--- Load configuration.
        try:
            homeDir = str(Path.home()).replace('\\', '/')
            configDir = f'{homeDir}/.pywriter/novelyst/config'
        except:
            configDir = '.'
        self.iniFile = f'{configDir}/editor.ini'
        self.configuration = Configuration(SETTINGS, OPTIONS)
        self.configuration.read(self.iniFile)
        self.kwargs = {}
        self.kwargs.update(self.configuration.settings)
        self.kwargs.update(self.configuration.options)

        # Add the "Edit" command to novelyst's "Scene" menu.
        self._ui.sceneMenu.add_separator()
        self._ui.sceneMenu.add_command(label=_('Edit'), underline=0, command=self._edit_scene)
        self._ui.tv.tree.bind('<Double-1>', self._edit_scene)
        self._ui.tv.tree.bind('<Return>', self._edit_scene)

        self.sceneEditors = {}
        try:
            path = os.path.dirname(sys.argv[0])
            if not path:
                path = '.'
            self._icon = tk.PhotoImage(file=f'{path}/icons/{ICON}.png')
        except:
            self._icon = None

        # Configure the editor box.
        SceneEditor.colorMode = int(self.kwargs['color_mode'])
        SceneEditor.liveWordCount = self.kwargs['live_wordcount']

    def _edit_scene(self, event=None):
        """Create a scene editor window with a menu bar, a text box, and a status bar."""
        try:
            nodeId = self._ui.tv.tree.selection()[0]
            if nodeId.startswith(self._ui.tv.SCENE_PREFIX):
                # A scene is selected
                if self._ui.isLocked:
                    messagebox.showinfo(APPLICATION, _('Cannot edit scenes, because the project is locked.'))
                    return

                scId = nodeId[2:]
                if scId in self.sceneEditors and self.sceneEditors[scId].isOpen:
                    self.sceneEditors[scId].lift()
                    return

                self.sceneEditors[scId] = SceneEditor(self, self._ui, scId, self.kwargs['window_geometry'], icon=self._icon)

        except IndexError:
            # Nothing selected
            pass

    def on_close(self, event=None):
        """Actions to be performed when a project is closed.
        
        Close all open scene editor windows. 
        """
        for scId in self.sceneEditors:
            if self.sceneEditors[scId].isOpen:
                self.sceneEditors[scId].on_quit()

    def on_quit(self, event=None):
        """Actions to be performed when novelyst is closed."""
        self.on_close()

        #--- Save project specific configuration
        self.kwargs['color_mode'] = SceneEditor.colorMode
        self.kwargs['live_wordcount'] = SceneEditor.liveWordCount
        for keyword in self.kwargs:
            if keyword in self.configuration.options:
                self.configuration.options[keyword] = self.kwargs[keyword]
            elif keyword in self.configuration.settings:
                self.configuration.settings[keyword] = self.kwargs[keyword]
        self.configuration.write(self.iniFile)

