# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'test_session_1'
copyright = '2026, Chheng Lydiya'
author = 'Chheng Lydiya'
release = '0.3'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Options for LaTeX / PDF output ------------------------------------------

latex_engine = 'xelatex'
latex_documents = [
    ('index', 'test_session_1.tex', 'Test Session 1 — Stability Analysis',
     'Chheng Lydiya', 'manual'),
]
latex_elements = {
    'preamble': r'''
\usepackage{graphicx}
''',
    'figure_align': 'H',
}
