"""Sphinx configuration file for pyBusPirateLite documentation."""

import os
import sys
from datetime import datetime

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath('..'))

# Project information
project = 'pyBusPirateLite'
copyright = f'{datetime.now().year}, Juergen Hasch'
author = 'Juergen Hasch'

# The full version, including alpha/beta/rc tags
release = '0.3.0'

# General configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosummary',
    'sphinx_rtd_theme',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# HTML theme settings
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_logo = '_static/logo.png'
html_favicon = '_static/favicon.ico'

# Theme options
html_theme_options = {
    'navigation_depth': 4,
    'titles_only': False,
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'both',
    'style_external_links': True,
    'style_nav_header_background': '#2980B9',
}

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'pyserial': ('https://pyserial.readthedocs.io/en/latest/', None),
}

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
} 