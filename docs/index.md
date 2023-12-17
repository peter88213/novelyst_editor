# nv_editor

The [noveltree](https://peter88213.github.io/noveltree/) Python program helps authors organize novels.  

*nv_editor* is a plugin providing a "plain text" section editor. 

![Screenshot](Screenshots/screen01.png)

## Features

- A simple text editor box without rich text display and search capability.
- Text is edited at the "raw markup" level. Markup tags are displayed as stored in the *yw7* file. Formatting tags are similar to those of HTML, but square brackets are used instead of pointed brackets.
- Multiple section editor windows.
- Word count is displayed and updated either live or on demand.
- The application is ready for internationalization with GNU gettext. A German localization is provided. 
- Editor features:
    - Text selection.
    - Copy/Cut/Paste to/from the clipboard.
    - Undo/Redo.
    - Key shortcuts for bold and italic formatting.
    - Create a new section after the current one.
    - Split the section at the cursor position.
    - Navigation to the next or previous section.
    
## Requirements

- [noveltree](https://peter88213.github.io/noveltree/) version 1.0+

## Download and install

[Download the latest release (version 5.3.0)](https://github.com/peter88213/nv_editor/raw/main/dist/nv_editor_v5.3.0.zip)

- Extract the "nv_editor_v5.3.0" folder from the downloaded zipfile "nv_editor_v5.3.0.zip".
- Move into this new folder and launch **setup.pyw**. This installs the plugin for the local user.

---

[Changelog](changelog)

## Usage

See the [instructions for use](usage)

## Credits

- The icons are made using the free *Pusab* font by Ryoichi Tsunekawa, [Flat-it](http://flat-it.com/).

## License

This is Open Source software, and the *nv_editor* plugin is licensed under GPLv3. See the
[GNU General Public License website](https://www.gnu.org/licenses/gpl-3.0.en.html) for more
details, or consult the [LICENSE](https://github.com/peter88213/nv_editor/blob/main/LICENSE) file.
