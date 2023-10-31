"""A multi-section "plain text" editor plugin for novelyst.

Requires Python 3.6+
Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/novelyst_editor
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""
import os
import sys
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import webbrowser
from nveditorlib.nv_editor_globals import *
from nveditorlib.section_editor import SectionEditor
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
    """novelyst multi-section "plain text" editor plugin class.
    
    Public methods:
        on_close() -- Actions to be performed when a project is closed.       
        on_quit() -- Actions to be performed when novelyst is closed.
        open_node() -- Create a section editor window with a menu bar, a text box, and a status bar.     
    """
    VERSION = '@release'
    NOVELYST_API = '5.0'
    DESCRIPTION = 'A multi-section "plain text" editor'
    URL = 'https://peter88213.github.io/novelyst_editor'
    _HELP_URL = 'https://peter88213.github.io/novelyst_editor/usage'

    def install(self, ui):
        """Add a submenu to the main menu.
        
        Positional arguments:
            ui -- reference to the NovelystTk instance of the application.
        """
        self._ui = ui

        #--- Load configuration.
        try:
            homeDir = str(Path.home()).replace('\\', '/')
            configDir = f'{homeDir}/.novelyst/config'
        except:
            configDir = '.'
        self.iniFile = f'{configDir}/editor.ini'
        self.configuration = Configuration(SETTINGS, OPTIONS)
        self.configuration.read(self.iniFile)
        self.kwargs = {}
        self.kwargs.update(self.configuration.settings)
        self.kwargs.update(self.configuration.options)

        # Add the "Edit" command to novelyst's "Section" menu.
        self._ui.sectionMenu.add_separator()
        self._ui.sectionMenu.add_command(label=_('Edit'), underline=0, command=self.open_node)

        # Add an entry to the Help menu.
        self._ui.helpMenu.add_command(label=_('Editor plugin Online help'), command=lambda: webbrowser.open(self._HELP_URL))

        # Set window icon.
        self.sectionEditors = {}
        try:
            path = os.path.dirname(sys.argv[0])
            if not path:
                path = '.'
            self._icon = tk.PhotoImage(file=f'{path}/icons/{ICON}.png')
        except:
            self._icon = None

        # Configure the editor box.
        SectionEditor.colorMode = int(self.kwargs['color_mode'])
        SectionEditor.liveWordCount = self.kwargs['live_wordcount']

    def open_node(self, event=None):
        """Create a section editor window with a menu bar, a text box, and a status bar."""
        try:
            nodeId = self._ui.tv.tree.selection()[0]
            if nodeId.startswith(SECTION_PREFIX):
                if self._ui.novel.sections[nodeId].stageLevel is not None:
                    return

                # A section is selected
                if self._ui.isLocked:
                    messagebox.showinfo(APPLICATION, _('Cannot edit sections, because the project is locked.'))
                    return

                if nodeId in self.sectionEditors and self.sectionEditors[nodeId].isOpen:
                    self.sectionEditors[nodeId].lift()
                    return

                self.sectionEditors[nodeId] = SectionEditor(self, self._ui, nodeId, self.kwargs['window_geometry'], icon=self._icon)

        except IndexError:
            # Nothing selected
            pass

    def on_close(self, event=None):
        """Actions to be performed when a project is closed.
        
        Close all open section editor windows. 
        """
        for scId in self.sectionEditors:
            if self.sectionEditors[scId].isOpen:
                self.sectionEditors[scId].on_quit()

    def on_quit(self, event=None):
        """Actions to be performed when novelyst is closed."""
        self.on_close()

        #--- Save project specific configuration
        self.kwargs['color_mode'] = SectionEditor.colorMode
        self.kwargs['live_wordcount'] = SectionEditor.liveWordCount
        for keyword in self.kwargs:
            if keyword in self.configuration.options:
                self.configuration.options[keyword] = self.kwargs[keyword]
            elif keyword in self.configuration.settings:
                self.configuration.settings[keyword] = self.kwargs[keyword]
        self.configuration.write(self.iniFile)

