import typing as t

import re
import hashlib

from poznamkovac.konvertor import vytvorit_poznamky
from poznamkovac.md import OBSAH


Nadpis = t.TypedDict("Nadpis", {
    "id": t.NotRequired[int],
    "level": int,
    "title": str,
    "content": str
})
"""Typ pre JSON nadpisu"""

ListDict = list[dict[str, t.Any]]
"""Typ pre list dictov."""

PRESKOCIT_OBSAH = (OBSAH,)
"""
    Všetok obsah nadpisu ktorý zodpovedá jednému z prvkov
    v tomto zozname nebude zahrnutý v JSON pojmovej mapy
"""

NADPISY_REGEX = re.compile(r'^(#+)\s?([^#\n]+)\s*([^#]+)\s*', flags=re.MULTILINE | re.DOTALL)
"""Regulárny výraz pre hľadanie nadpisov v markdown texte a ich obsahu"""



def generovat_farbu(cislo: int) -> str:
    h_md5 = hashlib.md5()

    h_md5.update(str(cislo).encode('utf-8'))
    hash_hex = h_md5.hexdigest()

    return f'#{hash_hex[:6]}'



def vytvorit_json_nadpisov(markdown_text: str) -> t.List[Nadpis]:
    """
        Táto funkcia konvertuje markdown text na JSON nadpisov
    """

    vysledky: list[tuple[str, str, str]] = NADPISY_REGEX.findall(markdown_text)
    """Všetky zhody regulárneho výrazu pre nadpisy v texte"""

    json_nadpisy: t.List[Nadpis] = []
    """Výsledné JSON nadpisov."""


    for vysledok in vysledky:
        level, titulok, obsah = len(vysledok[0]), vysledok[1].strip(), vysledok[2].strip()

        if obsah in PRESKOCIT_OBSAH:
            continue


        poznamky_html = vytvorit_poznamky(obsah)
        json_nadpisy.append({
            'level': level,
            'title': titulok,
            'content': poznamky_html,
        })


    return json_nadpisy



def vytvorit_vis_json(json_nadpisy: t.List[Nadpis]) -> t.Dict[str, ListDict]:
    """
        Vytvorí JSON pre vis.js z JSON mapy nadpisov
    """
    
    bunky: ListDict = []
    """Zoznam buniek ("nodes")"""
    spojenia: ListDict = []
    """Zoznam prepojení medzi bunkami ("edges")"""
    tooltipy: ListDict = []
    """Zoznam tooltipov (pre Tippy)"""


    zasobnik = []
    """Zásobník obsahuje nadpisy, ktoré ešte nemajú uzatvorený obsah (t. j.: neobsahujú žiadne ďalšie nadpisy)."""

    for nadpis in json_nadpisy:
        id_bunky = len(bunky) + 1

        # Ak obsah nadpisu nie je prázdny, pridáme ho do tooltipov:
        if not re.match(r'^\s*$', nadpis['content']):
            tooltipy.append({
                'id': id_bunky,
                'content': nadpis['content']
            })

        # Keď nájdeme nadpis, ktorý má rovnakú alebo nižšiu úroveň, uzavrieme predchádzajúci nadpis.
        while zasobnik and zasobnik[-1]['level'] >= nadpis['level']:
            zasobnik.pop()

        # Ak zásobník nie je prázdny, pridáme spojenie od posledného nadpisu v zásobníku k aktuálnemu nadpisu
        if zasobnik:
            spojenia.append({
                'from': zasobnik[-1]['id'],
                'to': id_bunky
            })

        # Pridáme aktuálny nadpis do zásobníka:
        zasobnik.append({'id': id_bunky, 'level': nadpis['level']})

        # Pridáme aktuálny nadpis do zoznamu buniek:
        bunky.append({
            'id': id_bunky,
            'label': nadpis['title'],
            'level': nadpis['level'],
            'color': generovat_farbu(nadpis['level'])
        })

    return {
        'bunky': bunky,
        'spojenia': spojenia,
        'tooltipy': tooltipy
    }


def vytvorit_pojmovu_mapu(markdown_text: str) -> t.Dict[str, ListDict]:
    """
        Táto funkcia vytvorí finálny JSON pojmovej mapy (pre vis.js) z markdown textu poznámok.
    """

    return vytvorit_vis_json(vytvorit_json_nadpisov(markdown_text))
