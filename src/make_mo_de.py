"""Generate a German translation file for GNU gettext.

This script is for the Windows Explorer context menu
as specified by the ".reg" file to generate. 

- Generate the language specific 'reg.mo' dictionary.

Usage: 
reg_make_mo_de.py

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/novelyst_editor
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import sys
from shutil import copyfile
sys.path.insert(0, f'{os.getcwd()}/../../PyWriter/src')
import msgfmt

APP = 'novelyst_editor'
PO_PATH = '../i18n/de.po'
MO_PATH = f'../i18n/locale/de/LC_MESSAGES/{APP}.mo'
MO_COPY = f'../../novelyst/src/locale/de/LC_MESSAGES/{APP}.mo'


def main():
    msgfmt.make(PO_PATH, MO_PATH)
    copyfile(MO_PATH, MO_COPY)


if __name__ == '__main__':
    main()
