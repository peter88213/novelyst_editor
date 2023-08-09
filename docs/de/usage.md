[Project homepage](https://peter88213.github.io/novelyst_editor)

--- 

A simple [novelyst](https://peter88213.github.io/novelyst/) multi-scene editor plugin based on the *tkinter.scrolledtext* widget.

---

# Installation

If [novelyst](https://peter88213.github.io/novelyst/) is installed, the setup script auto-installs the *novelyst_editor* plugin in the *novelyst* plugin directory.

The plugin adds an **Bearbeiten** entry to the *novelyst* **Abschnitt**-Menü, and an **Editor-Plugin Online-Hilfe** entry to the **Hilfe**-Menü.  

---

# Operation

---

## Launch the scene editor

- Open a scene editor window by double-clicking on a scene or via the **Abschnitt > Bearbeiten**-Menü entry when a scene is selected, or by hitting the *Enter* key.
- If the project is locked, editor windows cannot be opened.
- If you choose a scene already open, the window will be brought to the foreground.

---

## Select text

- Select a word via double-clicking.
- Select a paragraph via triple-clicking.
- Extend the selection via **Shift-Arrow**.
- Extend the selection to the next word via **Ctrl-Shift-Arrow**.
- **Ctrl-A** selects the whole text.

---

## Kopieren/Einfügen text

- **Ctrl-C** copies the selected text to the clipboard.
- **Ctrl-X** cuts the selected text and moves it to the clipboard.
- **Ctrl-V** pastes the clipboard text content to the cursor position.

---

## Format text

- **Ctrl-I** places "Kursiv" markup around the selected text or at the cursor. If the selection is already italic, remove markup.
- **Ctrl-B** places "Fett" markup around the selected text or at the cursor. If the selection is already bold, remove markup.
- **Ctrl-M** removes "Fett" and "Kursiv" markup from the selection.

*The operations described above do not take effect on markup outsides the selection. Be sure not to nest markup by accident.*


### A note about formatting text

It is assumed that very few types of text markup are needed for a novel text:

- *Emphasized* (usually shown as italics).
- *Strongly emphasized* (usually shown as capitalized).
- *Citation* (paragraph visually distinguished from body text).

When exporting to ODT format, *novelyst* replaces these formattings as follows: 

- Text with `[i]Kursiv markup[/i]` is formatted as *Emphasized*.
- Text with `[b]Fett markup[/b]` is formatted as *Strongly emphasized*. 
- Paragraphs starting with `> ` are formatted as *Quote*.

---

## Undo/Redo

- **Ctrl-Z** undoes the last editing. Multiple undo is possible.
- **Ctrl-Y** redoes the last undo. Multiple redo is possible.

---

## Split a scene

Via **Datei > An der Cursorposition teilen** or **Ctrl-Alt-S** you can split the scene at the cursor position. 

- Alle the text from the cursor position is cut and pasted into a neuly created scene. 
- The neu scene is placed after the currently edited scene.
- The neu scene is appended to the currently edited scene.
- The neu scene has the same status as the currently edited scene.  
- The neu scene is of the same type as the currently edited scene.  
- The neu scene has the same viewpoint character as the currently edited scene.  
- The editor loads the neuly created scene.

---

## Create a scene

Via **Datei > Abschnitt erzeugen** or **Ctrl-Alt-N** you can create a scene. 

- The neu scene is placed after the currently edited scene.
- The neu scene is of the same type as the currently edited scene.  
- The editor loads the neuly created scene.

---

## Wortzählung

- The scene word count is displayed at the status bar at the bottom of the window.
- By default, word count is updated manually, either by pressing the **F5** key, or via the **Wortzählung > Aktualisieren**-Menü entry.
- The word count can be updated "live", i.e. just while entering text. This is enabled via the **Wortzählung > Laufende Aktualisierung einschalten**-Menü entry. 
- Live update is disabled by the **Wortzählung > Laufende Aktualisierung ausschalten**-Menü entry. 

**Please note**

*Live updating the word count is resource intensive and may slow down the program when editing big scenes. This is why it's disabled by default.*

---

## Änderungen übernehmen

- You can apply changes to the scene with **Ctrl-S**. Then "Modified" status is displayed in *novelyst*.
- If the project is locked in *novelyst*, you will be asked to unlock it before changes can be applied.

---

## Beenden 

- You can exit via **Datei > Beenden**, or with **Ctrl-Q**.
- When exiting the program, you will be asked for applying changes.

---

# License

This is Open Source software, and the *novelyst_editor* plugin is licensed under GPLv3. See the
[GNU General Public License website](https://www.gnu.org/licenses/gpl-3.0.en.html) for more
details, or consult the [LICENSE](https://github.com/peter88213/novelyst_editor/blob/main/LICENSE) file.
