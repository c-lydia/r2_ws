# Configuration file for the Sphinx documentation builder.

project = 'session_2'
copyright = '2026, Chheng Lydiya'
author = 'Chheng Lydiya'
release = '0.3'

extensions = []

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

latex_engine = 'xelatex'
latex_documents = [
    ('index', 'session_2.tex', 'Test Session 2 — Navigation \\& Motor Mapping Analysis', 'Chheng Lydiya', 'manual'),
]
latex_elements = {
    'preamble': r'''
\usepackage{graphicx}
''',
    'figure_align': 'H',
}
