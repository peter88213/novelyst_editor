"""Provide global variables and functions.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/novelyst_editor
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import os
import sys
import locale
import gettext

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
ICON = 'eLogo32'
WINDOW_SIZE = '600x800'

__all__ = ['APPLICATION', 'PLUGIN', 'ICON', 'WINDOW_SIZE', '_']
