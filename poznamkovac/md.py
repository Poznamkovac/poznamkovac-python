from markdown import Markdown
from markdown.extensions.abbr import AbbrExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.toc import TocExtension
from markdown.extensions.sane_lists import SaneListExtension
from markdown.extensions.smarty import SmartyExtension
from markdown.extensions.meta import MetaExtension
from markdown.extensions.footnotes import FootnoteExtension

from pymdownx.arithmatex import arithmatex_fenced_format, arithmatex_inline_format
from pymdownx.superfences import SuperFencesCodeExtension, fence_div_format
from pymdownx.inlinehilite import InlineHiliteExtension


OBSAH = '[obsah]'
"""Označenie pre obsah (zoznam všetkých nadpisov a možnosť preklikávať sa na ne)."""



def konvertovat_markdown(markdown_text: str) -> tuple[str, dict[str, list[str]]]:
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
        FootnoteExtension(
            SUPERSCRIPT_TEXT="*[{}]",
            PLACE_MARKER="[vysvetlivky]",
            BACKLINK_TITLE="Naspäť na vysvetlivku č. %d v texte"
        ),
        SuperFencesCodeExtension(custom_fences=[
            {
                'name': "mermaid",
                'class': "mermaid",
                'format': fence_div_format
            },
            {
                'name': "mat",
                'class': "arithmatex",
                'format': arithmatex_fenced_format(which="generic")
            }
        ]),
        InlineHiliteExtension(custom_inline=[
            {
                'name': "mat",
                'class': "arithmatex",
                'format': arithmatex_inline_format(which="generic")
            }
        ])
    ], tab_length=2, output_format='html')

    return markdown_konvertor.convert(markdown_text), getattr(markdown_konvertor, "Meta", {})