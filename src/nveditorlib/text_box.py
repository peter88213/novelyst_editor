"""Provide a text editor widget for the novelyst editor plugin.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import re
import tkinter as tk
from tkinter import scrolledtext


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
