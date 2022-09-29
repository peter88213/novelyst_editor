"""Provide a rich text editor widget for the novelyst editor plugin.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import re
import tkinter as tk
from tkinter import scrolledtext
from tkinter import font as tkFont


class RichTextBox(scrolledtext.ScrolledText):
    """A text box applying formatting.
    
    Public methods:
    get_text -- Return the whole text from the editor box.
    set_text(text) -- Put text into the editor box and clear the undo/redo stack.
    count_words -- Return the word count.
    italic -- Make the selection italic.
    bold -- Make the selection bold.
    plain -- Remove formatting from the selection.

    Kudos to Bryan Oakley
    https://stackoverflow.com/questions/63099026/fomatted-text-in-tkinter
    """
    ITALIC_TAG = 'italic'
    BOLD_TAG = 'bold'

    YW_TAGS = ['i', '/i', 'b', '/b']
    TAGS = {'b': 'bold',
            'i': 'italic',
            }
    TAG_TO_YW = {
        ('tagon', 'italic'): '[i]',
        ('tagon', 'bold'): '[b]',
        ('tagoff', 'italic'): '[/i]',
        ('tagoff', 'bold'): '[/b]',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        defaultFont = tkFont.nametofont(self.cget('font'))

        boldFont = tkFont.Font(**defaultFont.configure())
        italicFont = tkFont.Font(**defaultFont.configure())

        boldFont.configure(weight='bold')
        italicFont.configure(slant='italic')

        self.tag_configure(self.BOLD_TAG, font=boldFont)
        self.tag_configure(self.ITALIC_TAG, font=italicFont)

    def set_text(self, text):
        """Convert text from yWriter markup and load it into the editor area."""
        taggedText = []
        tag = ''
        tagStack = ['']
        ywTag = ''
        while text:
            tagStartPos = text.find('[')
            if tagStartPos >= 0:
                tagEndPos = text.find(']')
                if tagEndPos >= 0:
                    ywTag = text[tagStartPos + 1:tagEndPos]
                    if ywTag in self.YW_TAGS:
                        chunk = text[0:tagStartPos]
                        text = text[tagEndPos + 1:]
                        tag = self.TAGS.get(ywTag, '')
                    else:
                        chunk = text[0:tagEndPos + 1]
                        text = text[tagEndPos + 1:]
                        tag = tagStack[-1]
                else:
                    chunk = text
                    text = ''
            else:
                chunk = text
                text = ''
            thisTag = tagStack.pop()
            if chunk:
                taggedText.append((chunk, thisTag))
            tagStack.append(tag)

        for entry in taggedText:
            text, tag = entry
            self.insert(tk.END, text, tag)

        self.edit_reset()
        # this is to prevent the user from clearing the box with Ctrl-Z

    def get_text(self):
        """Retrieve tagged text from the editor area and convert it to yWriter markup.
        
        Kudos to Stackoverflow user "j_4321"
        https://stackoverflow.com/questions/15724936/copying-formatted-text-from-text-widget-in-tkinter
        """
        taggedText = self.dump('1.0', tk.END, tag=True, text=True)
        textParts = []
        for key, value, __ in taggedText:
            if key == 'text':
                textParts.append(value)
            else:
                textParts.append(self.TAG_TO_YW.get((key, value), ''))
        return ''.join(textParts).strip(' \n')

    def count_words(self):
        """Return the word count."""
        text = re.sub('--|—|–|…', ' ', self.get('1.0', tk.END))
        # Make dashes separate words
        text = re.sub('\[.+?\]|\/\*.+?\*\/|\.|\,|-', '', text)
        # Remove comments and yWriter raw markup for word count; make hyphens join words
        wordList = text.split()
        return len(wordList)

    def italic(self, event=None):
        """Toggle italic for the selection."""
        self._set_format(tag='i')

    def bold(self, event=None):
        """Make the selection bold."""
        self._set_format(tag='b')

    def plain(self, event=None):
        """Remove formatting from the selection."""
        self._set_format()

    def _set_format(self, event=None, tag=''):
        if self.tag_ranges(tk.SEL):
            text = self.get(tk.SEL_FIRST, tk.SEL_LAST)
            currentTags = self._get_tags(tk.SEL_FIRST, tk.SEL_LAST)
            if self.TAGS.get(tag, '') in currentTags:
                tag = ''
                # Reset formatting.
            self._replace_selected(text, self.TAGS.get(tag, ''))

    def _replace_selected(self, text, tag):
        """Replace the selected passage by text; keep the selection."""
        self.mark_set(tk.INSERT, tk.SEL_FIRST)
        self.delete(tk.SEL_FIRST, tk.SEL_LAST)
        selFirst = self.index(tk.INSERT)
        self.insert(tk.INSERT, text, tag)
        selLast = self.index(tk.INSERT)
        self.tag_add(tk.SEL, selFirst, selLast)

    def _get_tags(self, start, end):
        """Get a set of tags between the start and end text mark.     
        
        Kudos to Bryan Oakley
        https://stackoverflow.com/questions/61661490/how-do-you-get-the-tags-from-text-in-a-tkinter-text-widget
        """
        index = start
        tags = []
        while self.compare(index, '<=', end):
            tags.extend(self.tag_names(index))
            index = self.index(f'{index}+1c')
        return set(tags)
