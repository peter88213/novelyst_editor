[Project homepage](https://peter88213.github.io/novelyst_editor)

--- 

A simple [novelyst](https://peter88213.github.io/novelyst/) multi-scene editor plugin based on the *tkinter.scrolledtext* widget.

### Installation

If [novelyst](https://peter88213.github.io/novelyst/) is installed, the setup script auto-installs the *novelyst_editor* plugin in the *novelyst* plugin directory.

The plugin adds an "Edit" entry to the *novelyst* "Scene" menu. 

## Operation

### Launch the scene editor

- Open a scene editor window by double-clicking on a scene or via the **Scene > Edit** menu entry when a scene is selected.
- If the project is locked, editor windows cannot be opened.
- If you double-click on a scene already open, the window will be brought to the foreground.

### Word count

- The scene word count is displayed at the status bar at the bottom of the window.
- By default, word count is updated manually, either by pressing the **F5** key, or via the **Word count > Update** menu entry.
- The word count can be updated "live", i.e. just while entering text. This is enabled via the **Word count > Enable live update** menu entry. 
- Live update is disabled by the **Word count > Disable live update** menu entry. 

**Please note**

*Live updating the word count is resource intensive and may slow down the program when editing big scenes. This is why it's disabled by default.*


### Apply changes

- You can apply changes to the scene with **Ctrl-S**. Then "Modified" status is displayed in *novelyst*.
- If the project is locked in *novelyst*, you will be asked to unlock it before changes can be applied.

### Exit 

- You can exit via **File > Exit**, or with **Ctrl-Q**.
- When exiting the program, you will be asked for applying changes.


