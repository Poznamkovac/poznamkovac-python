import re

from poznamkovac.bb_kod import konvertovat_bbkod
from poznamkovac.md import konvertovat_markdown



def vytvorit_poznamky(markdown_text: str) -> str:
    """
        Vytvorí HTML z BBCode/Markdown textu poznámok.

        Najskôr sa konvertuje Markdown, následne sa z tohto nového HTML
        ešte konvertuje BB kód.
    """

    obsah = konvertovat_markdown(markdown_text)
    obsah = konvertovat_bbkod(obsah)

    return obsah



def normalizovat_nadpisy(markdown_text: str) -> str:
    """
        Konvertuje prebytočné nadpisy na zoznamy a/alebo
        ich normalizuje (odstraňuje prebytočné mriežky, atď...).
    """

    regex = re.compile(r'^(#{7,})\s?([^#\n]+)\s*([^#]+)\s*', flags=re.MULTILINE | re.DOTALL)
    minus = 1
    """
        Ak obsah nadpisu (text do ďalšieho nadpisu) obsahuje `\n`,
        tak potom tento nadpis nemožno prevodiť na položku zoznamu.

        Nasledujúce položky sa preto posunú o `minus` levelov dozadu,
        aby sa zachovalo formátovanie zoznamu.
    """

    prva_polozka = True
    """Prvá položka v zozname bude mať dodatočný `\n` prefix, pre zachovanie formátovania"""


    def nahradit_nadpisy(vysledok: re.Match[str]) -> str:
        nonlocal minus
        nonlocal prva_polozka

        list_level, titulok, obsah = len(vysledok.group(1)) - 6, vysledok.group(2).strip(), vysledok.group(3).strip()


        # Nadpis nemôžno konvertovať:
        if '\n' in obsah:
            minus += 1

            return f"{'#' * 6} {titulok}\n\n{obsah}\n" # pôvodný text


        nove_vlakno = f"{('  ') * (list_level - minus)}- {titulok}" if list_level > 1 else f"- {titulok}"

        # Ak existuje obsah, t. j. nie je iba prázdny `str`, tak potom
        # za položku v zozname pripojíme aj definíciu (t. j. jednoriadkový obsah):
        if len(obsah) > 1:
            nove_vlakno += f" - {obsah}"


        novy_riadok = f"{nove_vlakno}\n"
        if prva_polozka:
            novy_riadok = '\n' + novy_riadok


        prva_polozka = False
        return novy_riadok


    # Nahradíme obsah pôvodného `markdown_text` s novým, konvertovaným obsahom
    return re.sub(regex, nahradit_nadpisy, markdown_text)
