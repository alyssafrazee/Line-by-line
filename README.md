Line-by-line
============

DISCLAIMER: Most of this code was taken from randy3k's [Enhanced-R](https://github.com/randy3k/Enhanced-R) plugin.

Line-by-line is a Sublime Text 2 plugin allowing users to run commands from Sublime in Terminal/iTerm easily with one keyboard shortcut.  This is an OSX-specific plugin (Enhanced-R suppords OSX, Windows, and Linux), but supports most coding languages that can be run in a REPL in the Terminal (rather than only R).  

`command-enter` sends either the current selection (in a ST2 file) or, if nothing is selected, the current line, to the Terminal or iTerm to be executed.  It's up to the user to make sure the appropriate REPL is running in the Terminal.

Typing `LBL: Choose Application` in the Command Palette allows the user to switch between Terminal and iTerm.
