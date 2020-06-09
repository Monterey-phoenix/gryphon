# texlive

#
# Modification History:
#   180803 David Shifflett
#     Changed clean to keep PDF file, erase TOC, added clean_all
#


DEPENDENCIES = mp_py_um.tex title.tex structure.tex screenshots/*

mp_py_um.pdf: $(DEPENDENCIES)
	pdflatex mp_py_um.tex
	pdflatex mp_py_um.tex

clean:
	rm -rf mp_py_um.aux mp_py_um.log mp_py_um.out mp_py_um.toc structure.aux

clean_all: clean
	rm -rf mp_py_um.pdf

