# -- Path setup --------------------------------------------------------------
import os
import sys

sys.path.append(os.path.abspath('..'))

import drb.drivers.zip

# -- Project information -----------------------------------------------------
project = 'ZIP driver for DRB'
copyright = '2021, GAEL Systems'
author = 'GAEL Systems Editor'

# The full version, including alpha/beta/rc tags
version = drb.drivers.zip.__version__
release = drb.drivers.zip.__version__

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosectionlabel',
]
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output --------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_show_sourcelink = False

# -- InterSphinx configuration ------------------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/', None),
}
# -- Napoleon configuration ---------------------------------------------------
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
# -- Autodoc configuration ----------------------------------------------------
autodoc_default_options = {
    'member-order': 'alphabetical',
    'undoc-members': False,
    'exclude-members': '__weakref__, __hash__, __slots__, __dict__,'
                       '__module__, __abstractmethods__, __init__'
}
