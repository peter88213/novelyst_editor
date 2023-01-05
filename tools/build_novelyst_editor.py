"""Build a python script for the novelyst distribution.
        
In order to distribute a single script without dependencies, 
this script "inlines" all modules imported from the pywriter package.

The PyWriter project (see see https://github.com/peter88213/PyWriter)
must be located on the same directory level as the novelyst project. 

For further information see https://github.com/peter88213/novelyst_editor
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import os
import sys
sys.path.insert(0, f'{os.getcwd()}/../../PyWriter/src')
import inliner

SRC = '../src/'
BUILD = '../test/'
SOURCE_FILE = f'{SRC}novelyst_editor.py'
TARGET_FILE = f'{BUILD}novelyst_editor.py'


def main():
    inliner.run(SOURCE_FILE, TARGET_FILE, 'nveditorlib', '../src/')
    print('Done.')


if __name__ == '__main__':
    main()
