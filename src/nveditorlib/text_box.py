"""Provide a text editor widget for the novelyst editor plugin.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/novelyst_editor
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import re
import tkinter as tk
from tkinter import ttk


class TextBox(tk.Text):
    """A text editor widget for yWriter raw markup.
    
    Public methods:
    get_text -- Return the whole text from the editor box.
    set_text(text) -- Put text into the editor box and clear the undo/redo stack.
    count_words -- Return the word count.
    italic -- Make the selection italic, or begin with italic input.
    bold -- Make the selection bold, or begin with bold input.
    plain -- Remove formatting from the selection.
    """
    _YW_TAGS = ('i', 'b')
    # Supported tags.

    def __init__(self, master=None, **kw):
        """Copied from tkinter.scrolledtext and modified (use ttk widgets).
        
        Extends the supeclass constructor.
        """
        self.frame = ttk.Frame(master)
        self.vbar = ttk.Scrollbar(self.frame)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)

        kw.update({'yscrollcommand': self.vbar.set})
        tk.Text.__init__(self, self.frame, **kw)
        self.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.vbar['command'] = self.yview

        # Copy geometry methods of self.frame without overriding Text
        # methods -- hack!
        text_meths = vars(tk.Text).keys()
        methods = vars(tk.Pack).keys() | vars(tk.Grid).keys() | vars(tk.Place).keys()
        methods = methods.difference(text_meths)

        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))

    def get_text(self, start='1.0', end=tk.END):
        """Return the whole text from the editor box."""
        text = self.get(start, end).strip(' \n')
        return text

    def set_text(self, text):
        """Put text into the editor box and clear the undo/redo stack."""
        self.insert(tk.END, text)
        self.edit_reset()
        # this is to prevent the user from clearing the box with Ctrl-Z

    def count_words(self):
        """Return the word count."""
        text = re.sub('--|—|–|…', ' ', self.get('1.0', tk.END))
        # Make dashes separate words
        text = re.sub('\[.+?\]|\/\*.+?\*\/|\.|\,|-', '', text)
        # Remove comments and yWriter raw markup for word count; make hyphens join words
        wordList = text.split()
        return len(wordList)

    def italic(self, event=None):
        """Make the selection italic, or begin with italic input."""
        self._set_format(tag='i')

    def bold(self, event=None):
        """Make the selection bold, or begin with bold input."""
        self._set_format(tag='b')

    def plain(self, event=None):
        """Remove formatting from the selection."""
        self._set_format()

    def _set_format(self, event=None, tag=''):
        """Insert an opening/closing pair of yWriter markup tags."""
        if tag:
            # Toggle format as specified by tag.
            if self.tag_ranges(tk.SEL):
                text = self.get(tk.SEL_FIRST, tk.SEL_LAST)
                if text.startswith(f'[{tag}]'):
                    if text.endswith(f'[/{tag}]'):
                        # The selection is already formatted: Remove markup.
                        text = self._remove_format(text, tag)
                        self._replace_selected(text)
                        return

                # Format the selection: Add markup.
                text = self._remove_format(text, tag)
                # to make sure that there is no nested markup of the same type
                self._replace_selected(f'[{tag}]{text}[/{tag}]')
            else:
                # Add markup to the cursor position.
                self.insert(tk.INSERT, f'[{tag}]')
                endTag = f'[/{tag}]'
                self.insert(tk.INSERT, endTag)
                self.mark_set(tk.INSERT, f'{tk.INSERT}-{len(endTag)}c')
        elif self.tag_ranges(tk.SEL):
            # Remove all markup from the selection.
            text = self.get(tk.SEL_FIRST, tk.SEL_LAST)
            for tag in self._YW_TAGS:
                text = self._remove_format(text, tag)
            self._replace_selected(text)

    def _replace_selected(self, text):
        """Replace the selected passage by text; keep the selection."""
        self.mark_set(tk.INSERT, tk.SEL_FIRST)
        self.delete(tk.SEL_FIRST, tk.SEL_LAST)
        selFirst = self.index(tk.INSERT)
        self.insert(tk.INSERT, text)
        selLast = self.index(tk.INSERT)
        self.tag_add(tk.SEL, selFirst, selLast)

    def _remove_format(self, text, tag):
        """Return text without opening/closing markup, if any."""
        if tag in self._YW_TAGS:
            finished = False
            while not finished:
                start = text.find(f'[{tag}]')
                if start >= 0:
                    end = text.find(f'[/{tag}]')
                    if  start < end:
                        text = f'{text[:start]}{text[start + 3:end]}{text[end + 4:]}'
                    else:
                        finished = True
                else:
                    finished = True
            return text
