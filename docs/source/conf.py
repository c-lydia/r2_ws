# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'target_setter'
copyright = '2026, Chheng Lydiya'
author = 'Chheng Lydiya'

# The full version, including alpha/beta/rc tags
release = '1.0'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.imgconverter', "sphinxcontrib.bibtex"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

bibtex_bibfiles = [
    "bib/software_architecture.bib",
    "bib/networking_distributed_system.bib",
    "bib/ros2_middleware.bib",
    "bib/control_system_signal.bib",
    "bib/robotic_modeling.bib",
]

bibtex_default_style = "ieeetr"

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
try:
    import sphinx_rtd_theme
    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
    html_theme_options = {
        'logo_only': False,
        'display_version': True,
        'prev_next_buttons_location': 'bottom',
    }
except Exception:
    # Fallback to alabaster when sphinx_rtd_theme is not installed
    html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Enable "Edit on GitHub" / repository links in the HTML output.
# Replace the placeholders below with your GitHub username and repository name.
html_context = {
    'display_github': True,  # Integrate GitHub
    'github_user': 'c-lydia',
    'github_repo': 'r2_ws',
    'github_version': 'main',
    'conf_py_path': '/docs/source/',  # Path in the repo to the docs root
}


# -- Options for LaTeX output ------------------------------------------------

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto, manual, or own class]).
latex_documents = [
    ('index', 'target_setter.tex', 'target\\_setter Documentation',
     'Chheng Lydiya', 'manual'),
]

# LaTeX engine to use
latex_engine = 'pdflatex'

# LaTeX elements
latex_elements = {
    'preamble': r'''
\usepackage{fancyvrb}
\usepackage{color}
\usepackage{listings}
\usepackage{fvextra}
\RecustomVerbatimEnvironment{Verbatim}{Verbatim}{breaklines=true, breakanywhere=true}
\lstset{
    basicstyle=\small\ttfamily,
    breaklines=true,
    breakatwhitespace=true,
    columns=flexible,
    frame=single,
    xleftmargin=0.5cm,
    xrightmargin=0.5cm,
    backgroundcolor=\color{gray!10}
}
''',
    'fontpkg': r'''
\usepackage{tgtermes}
\usepackage{tgheros}
\renewcommand\ttdefault{txtt}
''',
    'papersize': 'a4paper',
    'pointsize': '10pt',
}

# Syntax highlighting style
pygments_style = 'sphinx'

# Highlight language for code blocks without explicit language
highlight_language = 'bash'