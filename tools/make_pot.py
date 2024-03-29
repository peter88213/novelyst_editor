"""Generate a template file (pot) for message translation.

This script is for the Windows Explorer context menu
as specified by the ".reg" file to generate. 

For further information see https://github.com/peter88213/novelyst_editor
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import os
import sys
sys.path.insert(0, f'{os.getcwd()}/../../PyWriter/src')
from build_novelyst_editor import main
from build_novelyst_editor import TARGET_FILE
import pgettext

APP = 'novelyst_editor'
POT_FILE = f'../i18n/messages.pot'


def make_pot(version='unknown'):
    # Generate a complete script.
    main()

    # Generate a pot file from the script.
    if os.path.isfile(POT_FILE):
        os.replace(POT_FILE, f'{POT_FILE}.bak')
        backedUp = True
    else:
        backedUp = False
    try:
        pot = pgettext.PotFile(POT_FILE, app=APP, appVersion=version)
        pot.scan_file(TARGET_FILE)
        print(f'Writing "{pot.filePath}"...\n')
        pot.write_pot()
        return True

    except:
        if backedUp:
            os.replace(f'{POT_FILE}.bak', POT_FILE)
        print('WARNING: Cannot write pot file.')
        return False


if __name__ == '__main__':
    try:
        success = make_pot(sys.argv[1])
    except:
        success = make_pot()
    if not success:
        sys.exit(1)
