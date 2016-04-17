DIR = /home/plaice/soft/zebrackets-dir
SCRIPTS = ${DIR}/zebrackets-git/src
FONTS = ${DIR}/zebrackets-texmf
PYTHONSCRIPT = ${SCRIPTS}/zebrackets/zebraParser.py
BIBTEX = bibtex
LATEX = latex
PDFLATEX = pdflatex
PDFS = paper-tug.pdf T-tug.pdf
all: $(PDFS)

%.dvi: %.tex db.bib new.bib personal.bib type.bib
	(if [ "$$TEXMFHOME" = "" ] ; then \
	   export TEXMFHOME=${FONTS} ; \
         fi ; ${LATEX} $< ;  ${BIBTEX} `basename $< .tex` ; \
              ${LATEX} $< ;  ${LATEX} $< )

%.pdf: %.tex db.bib new.bib personal.bib type.bib zebib.tex
	(if [ "$$TEXMFHOME" = "" ] ; then \
	   export TEXMFHOME=${FONTS} ; \
         fi ; ${PDFLATEX} $< ;  ${BIBTEX} `basename $< .tex` ; \
              ${PDFLATEX} $< ;  ${PDFLATEX} $< )

%.tex: %.zbtex
	(if [ "$$TEXMFHOME" = "" ] ; then \
	   export TEXMFHOME=${FONTS} ; \
         fi ; \
	 if [ "$$PYTHONPATH" = "" ] ; then \
	 export PYTHONPATH=${SCRIPTS} ; \
         fi ; \
	 (python3 ${PYTHONSCRIPT} --input $< --output $@) )

.SECONDARY:

clean:
	(for i in ${PDFS} ; do \
	  rm -f `basename $$i .pdf`.aux ; \
	  rm -f `basename $$i .pdf`.bbl ; \
	  rm -f `basename $$i .pdf`.blg ; \
	  rm -f `basename $$i .pdf`.dvi ; \
	  rm -f `basename $$i .pdf`.log ; \
	  rm -f `basename $$i .pdf`.nav ; \
	  rm -f `basename $$i .pdf`.out ; \
	  rm -f `basename $$i .pdf`.pdf ; \
	  rm -f `basename $$i .pdf`.snm ; \
	  rm -f `basename $$i .pdf`.toc ; \
	  rm -f `basename $$i .pdf`.tex ; \
	  rm -f `basename $$i .pdf`.vrb ; \
	  done)
	rm -f zbtexfonts.log
