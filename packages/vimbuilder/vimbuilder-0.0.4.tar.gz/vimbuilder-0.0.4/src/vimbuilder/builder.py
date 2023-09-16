"""
Vim-help Sphinx builder.

Specialize TextBuilder to add tags and code blocks appropriate for Vim help
files. Hotlinks inside the file are not added since this would degrade
readability (Vim does not conceal hotlink destinations, both hotlink and
destination are one and the same). In addition, change italic/emphasis markers
from '*' to '_' so as not to interfere with Vim's tags.
"""

from __future__ import annotations

import re
from datetime import datetime
from os import path
from pathlib import Path
from typing import TYPE_CHECKING, Any, List

from docutils.nodes import table
from docutils.utils import column_width

from sphinx.addnodes import desc_signature
from sphinx.builders.text import TextBuilder
from sphinx.locale import __
from sphinx.util import logging
from sphinx.writers.text import TextTranslator, STDINDENT, MAXWIDTH

if TYPE_CHECKING:
    from docutils.nodes import Element, Node, document
    from sphinx.application import Sphinx

logger = logging.getLogger(__name__)

class VimHelpTranslator(TextTranslator):
    "Custom docutils/sphinx translator for vim help files"

    def __init__(self, document: document, builder: TextBuilder) -> None:
        super().__init__(document, builder)
        self.tag_prefix = self.config.vimhelp_tag_prefix
        self.tag_suffix = self.config.vimhelp_tag_suffix
        self.tag_filename = self.config.vimhelp_tag_filename
        self.tag_topic = self.config.vimhelp_tag_topic
        self.filename_suffix = self.config.vimhelp_filename_suffix
        self.filename_extension = self.config.vimhelp_filename_extension
        self.tags = set()
    def is_inside_table(self, node: Element) -> bool:
        while node.parent:
            if isinstance(node.parent, table):
                return True
            node = node.parent
        return False

    def add_text_nonl(self, text: str | List):
        # Each 'state' item is a list of (indent, str | lines)
        if self.states[-1] and self.states[-1][-1]:
            ilevel, lines = self.states[-1][-1]
            if type(lines) is list and not lines[-1]: # empty line
                lines.pop()
            self.states[-1].append((-sum(self.stateindent), text))

    def visit_literal_block(self, node: Element) -> None:
        if not self.is_inside_table(node):
            self.add_text_nonl('>')
        super().visit_literal_block(node)

    def depart_literal_block(self, node: Element) -> None:
        super().depart_literal_block(node)
        if not self.is_inside_table(node):
            self.add_text_nonl('<')

    def visit_inline(self, node: Element) -> None:
        if 'xref' in node['classes'] or 'term' in node['classes']:
            self.add_text('_')

    def depart_inline(self, node: Element) -> None:
        if 'xref' in node['classes'] or 'term' in node['classes']:
            self.add_text('_')

    def visit_emphasis(self, node: Element) -> None:
        self.add_text('_')

    def depart_emphasis(self, node: Element) -> None:
        self.add_text('_')

    def visit_literal_emphasis(self, node: Element) -> None:
        self.add_text('_')

    def depart_literal_emphasis(self, node: Element) -> None:
        self.add_text('_')

    def visit_title_reference(self, node: Element) -> None:
        self.add_text('_')

    def depart_title_reference(self, node: Element) -> None:
        self.add_text('_')

    def get_vim_tag(self, text: str) -> str:
        return f'*{self.tag_prefix}{text}{self.tag_suffix}*'

    def visit_document(self, node: Element) -> None:
        super().visit_document(node)
        # print(self.document.pformat())
        fpath = self.document['source']; assert fpath
        self.topic = Path(fpath).stem.replace(' ', '_')
        self.filename = self.topic + '.' + self.filename_extension
        tagname = self.get_vim_tag(self.filename + self.filename_suffix)
        timestamp = 'Last change: ' + datetime.today().strftime('%Y %b %d')
        spaces = ' ' * max(MAXWIDTH - len(tagname) - len(timestamp), 2)
        self.states[0].append((0, [tagname + spaces + timestamp, '']))

    def depart_document(self, node: Element) -> None:
        super().depart_document(node)
        footer = 'vim:tw=78:ts=8:ft=help:norl:'
        self.body += self.nl + footer

    def get_tag(self, node: Element) -> str | None:
        if self.is_inside_table(node):
            return None
        # If node is not intended to be in TOC then ignore it (ex.
        # __init__(), command options, etc.)
        if not node.hasattr('_toc_name') or not node['_toc_name']:
            return None
        if not node.parent and not node.parent.hasattr('desctype'):
            return None
        tag = node['_toc_name'].replace(' ', '_')
        if tag in self.tags:
            return None
        self.tags.add(tag)
        if self.tag_filename:
            tag += f'..{self.filename}'
        elif self.tag_topic:
            tag += f'..{self.topic}'
        return self.get_vim_tag(tag)

    def tag_fits(self, node: Element, tag: str) -> bool:
        return len(node.astext()) + len(tag) < MAXWIDTH - 2

    def visit_desc_signature(self, node: Element) -> None:
        self.cached_tag = None
        tag = self.get_tag(node)
        if tag and not self.tag_fits(node, tag):
            self.add_text_nonl(['', ' ' * (MAXWIDTH - len(tag)) + tag])
        else:
            self.cached_tag = tag
        super().visit_desc_signature(node)

    def depart_desc_signature(self, node: Element) -> None:
        super().depart_desc_signature(node)
        tag = self.cached_tag
        if tag and self.tag_fits(node, tag):
            text = ' ' * (MAXWIDTH - len(node.astext()) - len(tag)) + tag
            if type(self.states[-1]) is list and type(self.states[-1][-1][1]) is list:
                self.states[-1][-1][1][-1] += text
        self.cached_tag = None


class VimHelpBuilder(TextBuilder):
    name = 'vimhelp'
    format = 'text'
    epilog = __('The vim help files are in %(outdir)s.')

    allow_parallel = True
    default_translator_class = VimHelpTranslator

    def init(self) -> None:
        self.out_suffix = '.' + self.config.vimhelp_filename_extension
        super().init()
