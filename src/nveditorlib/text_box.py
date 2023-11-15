"""Provide a text editor widget for the novelyst editor plugin.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/novelyst_editor
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import re
import tkinter as tk
from tkinter import ttk

#--- Regular expressions for counting words and characters like in LibreOffice.
# See: https://help.libreoffice.org/latest/en-GB/text/swriter/guide/words_count.html

ADDITIONAL_WORD_LIMITS = re.compile('--|—|–')
# this is to be replaced by spaces, thus making dashes and dash replacements word limits

NO_WORD_LIMITS = re.compile('\<note\>.*?\<\/note\>|\<comment\>.*?\<\/comment\>|\<.+?\>')
# this is to be replaced by empty strings, thus excluding markup and comments from
# word counting, and making hyphens join words


class TextBox(tk.Text):
    """A text editor widget for novelyst raw markup.
    
    Public methods:
    get_text -- Return the whole text from the editor box.
    set_text(text) -- Put text into the editor box and clear the undo/redo stack.
    count_words -- Return the word count.
    emphasis -- Make the selection emphasized, or begin with emphasized input.
    strong_emphasis -- Make the selection strongly emphasized, or begin with strongly emphasized input.
    plain -- Remove formatting from the selection.
    """
    _TAGS = ('em', 'strong')
    # Supported tags.

    def __init__(self, master=None, **kw):
        """Copied from tkinter.scrolledtext and modified (use ttk widgets).
        
        Extends the supeclass constructor.
        """
        self.frame = ttk.Frame(master)
        self.vbar = ttk.Scrollbar(self.frame)
        self.vbar.pack(side='right', fill='y')

        kw.update({'yscrollcommand': self.vbar.set})
        tk.Text.__init__(self, self.frame, **kw)
        self.pack(side='left', fill='both', expand=True)
        self.vbar['command'] = self.yview

        # Copy geometry methods of self.frame without overriding Text
        # methods -- hack!
        text_meths = vars(tk.Text).keys()
        methods = vars(tk.Pack).keys() | vars(tk.Grid).keys() | vars(tk.Place).keys()
        methods = methods.difference(text_meths)

        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))

    def get_text(self, start='1.0', end='end'):
        """Return the whole text from the editor box."""
        text = self.get(start, end).strip(' \n')
        text = text.replace('\n', '')
        return text

    def set_text(self, text):
        """Put text into the editor box and clear the undo/redo stack."""
        text = text.replace('</p>', '</p>\n')
        self.insert('end', text)
        self.edit_reset()
        # this is to prevent the user from clearing the box with Ctrl-Z
        self.mark_set('insert', '1.0')

    def count_words(self):
        """Return the word count."""
        text = self.get('1.0', 'end').replace('\n', '')
        text = ADDITIONAL_WORD_LIMITS.sub(' ', text)
        text = NO_WORD_LIMITS.sub('', text)
        return len(text.split())

    def emphasis(self, event=None):
        """Make the selection emphasized, or begin with emphasized input."""
        self._set_format(tag='em')

    def strong_emphasis(self, event=None):
        """Make the selection strongly emphasized, or begin with strongly emphasized input."""
        self._set_format(tag='strong')

    def plain(self, event=None):
        """Remove formatting from the selection."""
        self._set_format()

    def _set_format(self, event=None, tag=''):
        """Insert an opening/closing pair of novelyst markup tags."""
        if tag:
            # Toggle format as specified by tag.
            if self.tag_ranges('sel'):
                text = self.get(tk.SEL_FIRST, tk.SEL_LAST)
                if text.startswith(f'<{tag}>'):
                    if text.endswith(f'</{tag}>'):
                        # The selection is already formatted: Remove markup.
                        text = self._remove_format(text, tag)
                        self._replace_selected(text)
                        return

                # Format the selection: Add markup.
                text = self._remove_format(text, tag)
                # to make sure that there is no nested markup of the same type
                self._replace_selected(f'<{tag}>{text}</{tag}>')
            else:
                # Add markup to the cursor position.
                self.insert('insert', f'<{tag}>')
                endTag = f'</{tag}>'
                self.insert('insert', endTag)
                self.mark_set('insert', f'insert-{len(endTag)}c')
        elif self.tag_ranges('sel'):
            # Remove all markup from the selection.
            text = self.get(tk.SEL_FIRST, tk.SEL_LAST)
            for tag in self._TAGS:
                text = self._remove_format(text, tag)
            self._replace_selected(text)

    def _replace_selected(self, text):
        """Replace the selected passage with text; keep the selection."""
        self.mark_set('insert', tk.SEL_FIRST)
        self.delete(tk.SEL_FIRST, tk.SEL_LAST)
        selFirst = self.index('insert')
        self.insert('insert', text)
        selLast = self.index('insert')
        self.tag_add('sel', selFirst, selLast)

    def _remove_format(self, text, tag):
        """Return text without opening/closing markup, if any."""
        if tag in self._TAGS:
            finished = False
            while not finished:
                start = text.find(f'<{tag}>')
                if start >= 0:
                    end = text.find(f'</{tag}>')
                    if  start < end:
                        text = f'{text[:start]}{text[start + len(tag) +2:end]}{text[end + len(tag) + 3:]}'
                    else:
                        finished = True
                else:
                    finished = True
            return text

    def clear(self):
        self.delete('1.0', 'end')
