SOURCEDIR = source
BUILDDIR = build/latex
SPHINXBUILD = sphinx-build
LATEXMK = latexmk

.PHONY: latexpdf clean

latexpdf:
	$(SPHINXBUILD) -b latex $(SOURCEDIR) $(BUILDDIR)
	cd $(BUILDDIR) && $(LATEXMK) -pdf target_setter.tex

clean:
	rm -rf build/*
