import markdown

from markdown.extensions.abbr import AbbrExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.toc import TocExtension
from markdown.extensions.sane_lists import SaneListExtension
from markdown.extensions.smarty import SmartyExtension
from markdown.extensions.meta import MetaExtension
from markdown.extensions.footnotes import FootnoteExtension

from pymdownx.superfences import SuperFencesCodeExtension


OBSAH = '[obsah]'
"""Označenie pre obsah (zoznam všetkých nadpisov a možnosť preklikávať sa na ne)."""



def konvertovat_markdown(markdown_text: str) -> str:
    """
        Konvertuje Markdown na HTML.
    """

    markdown_konvertor = markdown.Markdown(extensions=[
        AbbrExtension(),
        TableExtension(),
        TocExtension(anchorlink=True, marker=OBSAH),
        SaneListExtension(),
        SmartyExtension(),
        MetaExtension(),
        FootnoteExtension(),
        SuperFencesCodeExtension()
    ], tab_length=2)

    return markdown_konvertor.convert(markdown_text)