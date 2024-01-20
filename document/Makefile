PREFIX=/usr/local/teTeX/bin/

LATEX=pdflatex
BIBTEX=bibtexu
PDFLATEX=pdflatex
DOC=book
SRC=book.tex 

all: $(DOC).pdf

$(DOC).dvi: $(DOC).tex $(SRC) Makefile 
	-$(LATEX) $(DOC)
	-$(BIBTEX) $(DOC)
	-$(LATEX) $(DOC)
	-$(LATEX) $(DOC)

$(DOC).pdf: $(DOC).tex $(SRC) Makefile 
	-$(PDFLATEX) $(DOC)
	-$(BIBTEX) $(DOC)
	-$(PDFLATEX) $(DOC)
	-$(PDFLATEX) $(DOC)

clean:
	rm -f *.aux *.dvi *.idx *.ilg *.ind *.log *.toc *.out *.bak *~ \
	$(DOC).bbl $(DOC).blg $(DOC).ps $(DOC).spl $(DOC).pdf

