Line-by-line
============

DISCLAIMER: Most of this code was taken from randy3k's [Enhanced-R](https://github.com/randy3k/Enhanced-R) plugin.

UPDATE (2/5/14): Also check out Winston Chang's [SendText](https://github.com/wch/SendText)! His plugin pretty much does exactly what Line-by-line does. If I had seen SendText, I probably wouldn't have made Line-by-line, though upon reflection, I'm glad I did make it because I learned a lot.

--------

Line-by-line is a Sublime Text 2 plugin allowing users to run commands from Sublime in Terminal/iTerm easily with one keyboard shortcut.  This is an OSX-specific plugin (Enhanced-R suppords OSX, Windows, and Linux), but unlike Enhanced-R, it supports most coding languages that can be run in a REPL in the Terminal (not just R).  

`command-enter` sends either the current selection (in a ST2 file) or, if nothing is selected, the current line, to the Terminal or iTerm to be executed.  It's up to the user to make sure the appropriate REPL is running in the Terminal.

Typing `LBL: Choose Application` in the Command Palette allows the user to switch between Terminal and iTerm.

In R scripts, if you highlight the first line of a function and hit `command-d`, a roxygen2-style documentation template will pop up above the function. This is thanks to Karthik Ram. I copied his code, from the wonderful [RTools](https://github.com/karthik/Rtools) plugin, directly into this package because RTools sends code to the R app (not the Terminal). 
