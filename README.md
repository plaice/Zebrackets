# Zebrackets
Zebrackets project for striated parentheses and brackets in LaTeX documents for expressing mathematical formulas with more clarity.

The purpose of the project is to have a package with three main modules. 
* `zebraParser`: takes the input `.zetex` file, output `.tex` file and the `TEXMFHOME` directory names. It parses the input file and when necessary, calls other modules to create fonts or replace symbols.
* `zebraFont`: takes a list of arguments to create a *zebracket* font.
* `zebraFilter`: replaces the occurence of a normal parenthesis with a zebracket glyph, based on the parameters given.

## Status
1. Currently reviewing the algorithm of `zebraFilter` to ensure that the input arguments are handled and processed properly. 
2. We need to ensure consistency of terminology.
3. Standardize error handling and testing infrastructure. 
