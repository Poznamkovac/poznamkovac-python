from markdown import Markdown
from markdown.extensions.abbr import AbbrExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.toc import TocExtension
from markdown.extensions.sane_lists import SaneListExtension
from markdown.extensions.smarty import SmartyExtension
from markdown.extensions.meta import MetaExtension
from markdown.extensions.footnotes import FootnoteExtension

from pymdownx.superfences import SuperFencesCodeExtension, fence_div_format


OBSAH = '[obsah]'
"""Označenie pre obsah (zoznam všetkých nadpisov a možnosť preklikávať sa na ne)."""



def konvertovat_markdown(markdown_text: str) -> str:
    """
        Konvertuje Markdown na HTML.
    """

    markdown_konvertor = Markdown(extensions=[
        AbbrExtension(),
        TableExtension(),
        TocExtension(anchorlink=True, marker=OBSAH),
        SaneListExtension(),
        SmartyExtension(),
        MetaExtension(),
        FootnoteExtension(),
        SuperFencesCodeExtension(custom_fences=[{
            'name': "mermaid",
            'class': "mermaid",
            'format': fence_div_format
        }]),
    ], tab_length=2, output_format='html')

    return markdown_konvertor.convert(markdown_text)