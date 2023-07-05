import typing as t

import re

from poznamkovac.bb_kod import konvertovat_bbkod
from poznamkovac.md import konvertovat_markdown


IterNadpis = t.NamedTuple('IterNadpis', level=int, titulok=str, obsah=t.Text)
"""Typ pre raw nadpis"""

OBSAH_REGEX = re.compile(r'^(#+)\s?([^#\n]+)\s*([^#]+)\s*', flags=re.MULTILINE | re.DOTALL)
"""Regulárny výraz pre hľadanie nadpisov v markdown texte a ich obsahu"""



def normalizovat_nadpisy(markdown_text: str) -> str:
    """
        Konvertuje prebytočné nadpisy na zoznamy a/alebo
        ich normalizuje (odstraňuje prebytočné mriežky, atď...).
    """

    dozadu = 1
    """
        Ak obsah nadpisu (text do ďalšieho nadpisu) obsahuje `\n`,
        tak potom tento nadpis nemožno prevodiť na položku zoznamu.

        Nasledujúce položky sa preto posunú o `minus` levelov dozadu,
        aby sa zachovalo formátovanie zoznamu.
    """

    prva_polozka = True
    """Prvá položka v zozname bude mať dodatočný `\n` prefix, pre zachovanie formátovania"""


    def nahradit_nadpisy(vysledok: re.Match[str]) -> str:
        nonlocal dozadu
        nonlocal prva_polozka

        list_level, titulok, obsah = len(vysledok.group(1)), vysledok.group(2).strip(), vysledok.group(3).strip()


        if list_level <= 6:
            # nepotrebujeme normalizáciu
            dozadu = 1

            return f"{'#' * list_level} {titulok}\n\n{obsah}\n"

        if '\n' in obsah:
            # nadpis nemôžno konvertovať
            dozadu = list_level - 6

            return f"{'#' * 6} {titulok}\n\n{obsah}\n\n" # najvyšší možný nadpis


        nove_vlakno = f"{'  ' * (list_level - (dozadu + 6))}- {titulok}" if list_level > 1 else f"- {titulok}"

        # Ak existuje obsah, t. j. nie je iba prázdny `str`, tak potom
        # za položku v zozname pripojíme aj definíciu (t. j. jednoriadkový obsah):
        if obsah:
            nove_vlakno += f": {obsah}"


        novy_riadok = f"{nove_vlakno}\n"
        if prva_polozka:
            novy_riadok = '\n' + novy_riadok


        prva_polozka = False
        return novy_riadok


    # Nahradíme obsah pôvodného `markdown_text` s novým, konvertovaným obsahom
    return OBSAH_REGEX.sub(nahradit_nadpisy, markdown_text)



def pridat_novu_stranu(obsah: str) -> str:
    """
        Nahradí `[nova_strana]` s `<div class="nova-strana"></div>`.

        Pri zobrazení tlače sa v tomto bode vždy strana zlomí.
    """

    return obsah.replace("[nova_strana]", '<div class="nova-strana"></div>')



def vytvorit_poznamky(markdown_text: str, normalizovat: bool=True) -> tuple[str, dict[str, list[str]]]:
    """
        Vytvorí HTML z BBCode/Markdown textu poznámok.

        Najskôr sa konvertuje Markdown, následne sa z tohto nového HTML
        ešte konvertuje BB kód.

        Ak je `normalizovat == True`, tak potom sa nadpisy normalizujú (viď. `poznamkovac.konvertor.normalizovat_nadpisy`)
    """

    markdown_text = normalizovat_nadpisy(markdown_text) if normalizovat else markdown_text

    html, metadata = konvertovat_markdown(markdown_text)
    html = konvertovat_bbkod(html)
    html = pridat_novu_stranu(html)

    return html, metadata
