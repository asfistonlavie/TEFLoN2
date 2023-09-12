# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'TEFLoN2'
copyright = '2022, Corentin Marco'
author = 'Corentin Marco'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The nam of the Pygments (syntax highlighting)
pygments_style = 'sphinx'
highlight_language = "python"

#If true, 'todo' and 'todolst' produce output .....
todo_include_todos = False
 

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'

html_css_files = ['css/custom.css']

extensions = ['myst_parser']


html_static_path = ['_static']
