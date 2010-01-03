# -*- coding: utf-8 -*-

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.todo']
templates_path = ['_templates']
source_suffix = '.rst'
source_encoding = 'utf-8'
master_doc = 'index'
project = u'aursh'
copyright = u'2010, Piotr Husiatyński'
version = '2.0'
release = '1.9.99'

exclude_trees = []
#default_role = None
add_function_parentheses = True
add_module_names = True
#show_authors = False
pygments_style = 'sphinx'
#modindex_common_prefix = []

html_theme = 'default'
html_theme_options = {
    'footerbgcolor': '#FFFFFF',
    'footertextcolor': '#FFFFFF',
    'sidebarbgcolor': '#F0F0F0',
    'sidebartextcolor': '#4D4D4D',
    'sidebarlinkcolor': '#1793D1',
    'relbarbgcolor': '#333333',
    'relbartextcolor': '#FFFFFF',
    'relbarlinkcolor': '#1793D1',
    'bgcolor': '#FFFFF',
    'textcolor': '#343434',
    'linkcolor': '#1793D1',
    'headbgcolor': '',
    'headtextcolor': '',
    'headlinkcolor': '',
    'codebgcolor': '#2B2B2B',
    'codetextcolor': '#F5F5F5',
    #'bodyfont': '',
    #'headfont': '',
}
#html_theme_path = []
#html_title = None
#html_short_title = None
#html_logo = None
#html_favicon = None
html_static_path = ['_static']
#html_last_updated_fmt = '%b %d, %Y'
#html_use_smartypants = True
#html_sidebars = {}
#html_additional_pages = {}
#html_use_modindex = True
#html_use_index = True
#html_split_index = False
#html_show_sourcelink = True
#html_use_opensearch = ''
#html_file_suffix = ''
htmlhelp_basename = 'aurshdoc'
