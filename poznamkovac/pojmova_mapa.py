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
    hash_hex = hashlib.md5(str(cislo).encode('utf-8')).hexdigest()

    # Konvertovať HEX na int
    hash_int = [int(hash_hex[x:x + 2], 16) for x in range(0, len(hash_hex), 2)]

    # Konvertovať int na svetlú farbu
    svetla_farba = [hex(min(int(x * 0.75) + 75, 255))[2:].zfill(2) for x in hash_int]

    return f'#{"".join(svetla_farba[:3])}'



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


    # Premenná pre sledovanie aktuálneho čísla farby (pre rozdielne farby vetví na rovnakom leveli)
    aktualna_farba = 1

    for nadpis in json_nadpisy:
        id_bunky = len(bunky) + 1

        # Ak obsah nadpisu nie je prázdny, pridáme ho do tooltipov:
        if not re.match(r'^\s*$', nadpis['content']):
            tooltipy.append({
                'id': id_bunky,
                'content': nadpis['content']
            })


        # Keď nájdeme nadpis, ktorý má rovnakú alebo nižšiu úroveň, uzavrieme predchádzajúci nadpis:
        while zasobnik and zasobnik[-1]['level'] >= nadpis['level']:
            zasobnik.pop()

            # Zmena farby, keď prichádzame na novú vetvu rovnakej úrovne
            if zasobnik[-1]['level'] == nadpis['level']:
                aktualna_farba *= -1


        # Ak zásobník nie je prázdny, pridáme spojenie od posledného nadpisu v zásobníku k aktuálnemu nadpisu:
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

            # Číslo 4 vyústi v pestré a vyvážené farby.
            #
            # V maturite snáď nepotrebujem jednotku,
            # veď štvorka sa mi aj tak v živote hodí.
            # Kto by chcel byť v škole na potvorku,
            # tak radšej štvorka a nechť sa mi dobre chodí.
            #
            # Nechajme teda tých, čo sa trasú o jednotku,
            # nehádam sa s nimi o miesto na slnku.
            # Veď štvorka ma prevedie svetom celkom jemne,
            # uvidíme všetko, čo život dá mne.
            #
            # "Preboha, mládež, len to nezarecitujte predsedníčke!"
            'color': generovat_farbu(4 - aktualna_farba * nadpis['level'])
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
