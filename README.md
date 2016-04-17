# Zebrackets
Zebrackets project for striated parentheses and brackets in LaTeX documents for expressing mathematical formulas with more clarity.

The purpose of the project is to have a package with three main modules. 
* `zebraParser`: takes the input `.zbtex` file, output `.tex` file and the `TEXMFHOME` directory names. It parses the input file and when necessary, calls other modules to create fonts or replace symbols.
* `zebraFont`: takes a list of arguments to create a *zebracket* font.
* `zebraFilter`: replaces the occurence of a normal parenthesis with a zebracket glyph, based on the parameters given.

## Status
1. Software works.
2. Paper written.
3. Initial presentation for TUG 2016 (July, Toronto).
