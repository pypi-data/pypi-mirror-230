# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "pyjapi"
copyright = "2022, Jannis Mainczyk"
author = "Jannis Mainczyk"
from pyjapi.cli import __version__

release = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_automodapi.automodapi",
    "sphinx_automodapi.smart_resolver",
    "sphinxcontrib.programoutput",  # Dynamically generate script output
    "sphinx_click.ext",  # Generate documentation for click cli
    "sphinx.ext.graphviz",
    "sphinx.ext.inheritance_diagram",
    "sphinx.ext.coverage",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinxcontrib.images",  # include images as thumbnails in HTML output
    "sphinx_git",  # include excerpts from your git history
    "sphinxcontrib.apidoc",  # build apidoc during sphinx-build
    # 'sphinx.ext.ifconfig',
    # 'sphinxcontrib.mermaid',
    # 'sphinx_issues',
    # autosummary is required to be explicitly loaded by confluencebuilder
    # (see https://github.com/sphinx-contrib/confluencebuilder/issues/304)
    "sphinx.ext.autosummary",
    "sphinxcontrib.confluencebuilder",
    # Include Markdown Files (README, CHANGELOG, ...)
    "myst_parser",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

default_role = "py:obj"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_logo = "_static/logo.png"

# -- Options for Confluence Builder ------------------------------------------
# https://sphinxcontrib-confluencebuilder.readthedocs.io/
import os  # read confluence password from env

confluence_publish = True
confluence_server_url = "https://intern.iis.fhg.de/"
confluence_server_user = "mkj"
confluence_server_pass = os.getenv("CONF_PW")
confluence_parent_page = "libjapi clients"
confluence_space_name = "DOCS"

# Generic configuration.
confluence_page_hierarchy = True

# Publishing configuration.
confluence_disable_notifications = True
# confluence_purge = True

# -- Options for sphinx-automodapi -----------------------------------------------
# Doesn't seem to work with singlehtml builder

numpydoc_show_class_members = False  # supposedly required to prevent duplicate entries

# Name of the directory the automodsumm generated documentation ends up in.
# This directory path should be relative to the documentation root (e.g., same place as index.rst).
# Defaults to 'api'.
automodapi_toctreedirnm = "automodapi"

# Indicate whether to show inheritance diagrams by default.
# This can be overridden on a case by case basis with :inheritance-diagram: and :no-inheritance-diagram:.
# Defaults to True.
automodapi_inheritance_diagram = False

automodapi_writereprocessed = False
"""bool: Replace automodapi sections with Sphinx output for debugging purposes. [default: False]

Will cause automodapi to write files with any automodapi sections replaced with the content
Sphinx processes after automodapi has run.
The output files are not actually used by sphinx, so this option is only for figuring
out the cause of sphinx warnings or other debugging.
"""

automodsumm_writereprocessed = False
"""bool: replace automodsumm sections with Sphinx output for debugging purposes. [default: False]"""

automodsumm_inherited_members = False
"""bool: Include members of base classes in documentation. [default: False]"""

# -- Options for intersphinx -------------------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pytest": ("https://docs.pytest.org/en/latest/", None),
}

# -- Options for sphinxcontrib-images ----------------------------------------
# https://sphinxcontrib-images.readthedocs.io/en/latest/
images_config = {
    "backend": "LightBox2",  # default: 'LightBox2'
    "override_image_directive": False,  # default: False
    "cache_path": "_images",  # default: '_images'
    "requests_kwargs": {},  # default: {}
    "default_image_width": "100%",  # default: '100%'
    "default_image_height": "auto",  # default: 'auto'
    "default_group": None,  # default: None
    "default_show_title": False,  # default: False (broken)
    "download": True,  # default: True
}

# -- Options for sphinx-git --------------------------------------------------
# https://sphinx-git.readthedocs.io/en/latest/using.html

# -- Options for sphinxcontrib-programoutput ---------------------------------
# https://sphinxcontrib-programoutput.readthedocs.io/

# A format string template for the output of the prompt option to command-output. default: '$ {command}\n{output}'
# Available variables: {command} {output} {returncode}
# programoutput_prompt_template = "$ {command}\n{output}"

# -- Options for autodoc -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html

# This value selects what content will be inserted into the main body of an autoclass directive.
# The possible values are:
#     "class": Only the class’ docstring is inserted. (default)
#     "init": Only the __init__ method’s docstring is inserted.
#     "both": Both the class’ and the __init__ method’s docstring are concatenated and inserted.
#
autoclass_content = "both"

# This value selects if automatically documented members are:
#     'alphabetical': sorted alphabetical, (default)
#     'groupwise': by member type
#     'bysource': or by source order
# Note that for source order, the module must be a Python module with the source code available.
#
autodoc_member_order = "groupwise"

# The default options for autodoc directives. They are applied to all autodoc directives automatically.
# It must be a dictionary which maps option names to the values. Setting None or True to the value is
# equivalent to giving only the option name to the directives.
#
# The supported options are 'members', 'member-order', 'undoc-members', 'private-members',
# 'special-members', 'inherited-members', 'show-inheritance', 'ignore-module-all' and
# 'exclude-members'.
#
autodoc_default_options = {
    # 'members': None,
    # 'member-order': 'bysource',
    "undoc-members": True,
    # 'private-members': True,
    # 'special-members': True,
    # 'inherited-members': True,
    "show-inheritance": False,
    "ignore-module-all": True,
    "imported-members": False,
    "exclude-members": None,
}

# This value controls the docstrings inheritance.
#
# True: the docstring for classes or methods, if not explicitly set, is inherited from parents. (default)
# False: docstrings are not inherited.
#
autodoc_inherit_docstrings = True

# -- Options for sphinxcontrib-apidoc ----------------------------------------
# https://pypi.org/project/sphinxcontrib-apidoc/

# The path to the module to document.
#
# Path to a Python package. This path can be:
# - a path relative to the documentation source directory
# - an absolute path.
apidoc_module_dir = "../../src/pyjapi"

# The output directory.
#
# If it does not exist, it is created.
# This path is relative to the documentation source directory.
# default: 'api'
apidoc_output_dir = "apidoc"

# An optional list of modules to exclude.
#
# These should be paths relative to apidoc_module_dir. fnmatch-style wildcards are supported.
# Optional, defaults to [].
apidoc_excluded_paths = ["tests"]

# Put documentation for each module on its own page.
#
# Otherwise there will be one page per (sub)package.
# Optional, defaults to False.
apidoc_separate_modules = True

# Filename for a table of contents file.
#
# Defaults to modules.
# If set to False, apidoc will not create a table of contents file.
apidoc_toc_file = False

# When set to True, put module documentation before submodule documentation.

# Optional, defaults to False.
apidoc_module_first = True

# Extra arguments which will be passed to sphinx-apidoc.
#
# These are placed after flags and before the module name.
# Optional, defaults to [].
# apidoc_extra_args = []
