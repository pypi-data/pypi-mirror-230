# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?= -E -a -n
#  -E	don't use a saved environment, always read all files
#  -a   write all files (default: only write new and changed files)
#  -n	nit-picky mode, warn about all missing references
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = ../build/docs
SPHINXPROJ 	  = pyjapi
PKGROOTDIR    = ../src/pyjapi
APIDOCOPTS    = -fTMe --implicit-namespaces
AUTOBUILDOPTS = --open-browser --watch ../README.md --watch ../src
AUTOBUILDDIR  = $(BUILDDIR)/live
# -f: overwrite already built rst files
# -d 4: set maximum toctree depth
# -E / --no-heading
# -e / --separate:
# -T / --no-toc: do not create a toc file (default filename: modules.rst)
# -M / --module-first:
# see http://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html
APIDOCDIR	  = apidoc
PYREVERSEARGS = --ignore=__init__,__main__.py --filter-mode=PUB_ONLY --output pdf
# -f, --filter-mode		Which attributes are displayed in class diagram [PUB_ONLY, ALL, SPECIAL, OTHER] (default: PUB_ONLY)
# -o, --output			Set output format [dot, pdf, png, ...] (default: dot)

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# custom targets
.PHONY: uml uml-ci apidoc live clean
uml: uml-ci
	@open $(BUILDDIR)/uml/*.pdf
uml-ci:
	@pyreverse -p "$(SPHINXPROJ)" $(PYREVERSEARGS) "$(PKGROOTDIR)"
	@mkdir -p $(BUILDDIR)/uml
	@mv packages_$(SPHINXPROJ).pdf $(BUILDDIR)/uml/
	@mv classes_$(SPHINXPROJ).pdf $(BUILDDIR)/uml/
apidoc:
	@sphinx-apidoc $(APIDOCOPTS) -o "$(SOURCEDIR)/$(APIDOCDIR)" "$(PKGROOTDIR)"
	@# remove module / package from rst headers
	@-for f in $(SOURCEDIR)/$(APIDOCDIR)/*.rst; do\
        perl -pi -e 's/(module|package)$$// if $$. == 1' $$f ;\
    done
live:
	sphinx-autobuild $(SPHINXOPTS) $(AUTOBUILDOPTS) "$(SOURCEDIR)" "$(AUTOBUILDDIR)"


clean:
	@rm -rf $(SOURCEDIR)/automodapi
	@rm -rf $(SOURCEDIR)/$(APIDOCDIR)

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
