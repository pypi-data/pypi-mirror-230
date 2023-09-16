"""
A Sphinx extension to add Vim help file generation support.
"""

from sphinx.application import Sphinx
from typing import Any
from vimbuilder.builder import VimHelpBuilder

def setup(app: Sphinx) -> dict[str, Any]:
    app.add_builder(VimHelpBuilder)

    app.add_config_value('vimhelp_tag_prefix', '', 'env')
    app.add_config_value('vimhelp_tag_suffix', '', 'env')
    app.add_config_value('vimhelp_tag_filename', True, 'env')
    app.add_config_value('vimhelp_tag_topic', False, 'env')
    app.add_config_value('vimhelp_filename_suffix', '', 'env')
    app.add_config_value('vimhelp_filename_extension', 'txt', 'env')

    return {
        'version': 'builtin',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
