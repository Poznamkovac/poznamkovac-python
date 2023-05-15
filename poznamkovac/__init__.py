import json

from jsonmerge import merge
from pathlib import Path


KORENOVA_CESTA = Path(__file__).parent.absolute()
"""Koreňová cesta k zdrojovému kódu Poznámkovača"""

SABLONY_CESTA = KORENOVA_CESTA / "sablony"
"""Cesta ku Jinja2 šablónam"""

POZNAMKY_CESTA = KORENOVA_CESTA.parent / "poznamky"
"""Cesta k priečinku s poznámkami"""
VYSTUPNA_CESTA = KORENOVA_CESTA.parent / "site"
"""Výstupná cesta, t. j. kde budú umiestnené konvertované poznámky, HTML a statické súbory."""


from poznamkovac.konvertor import vytvorit_poznamky
from poznamkovac.sablony import ZAKLAD_POZNAMOK, JINJA_ENV, konvertovat_sablonu
from poznamkovac.pojmova_mapa import vytvorit_pojmovu_mapu



def nacitat_json_konstanty(poznamky_cesta: Path) -> dict:
    """
        Načíta všetky JSON kontexty pre Jinju.

        Kontexty sa načítavajú z akéhokoľvek `.json` súboru, ktorý je prítomný v priečinku poznámok (`POZNAMKY_CESTA`).
        Tieto kontexy budú globálne prítomné v Jinja šablónach, prostredníctvom premennej `k`.

        Napr.:

        `poznamky/abc/autori.json`:

        ```json
        {
            "sjl": {
                "autori": {
                    "JGT": "**Jozef Gregor Tajovský** - vedúca osobnosť druhej vlny slovenského literárneho realizmu (*kritického realizmu; prvou bol opisný realizmus*).",
                    "MK": "**Martin Kukučín** - vlastným menom *MUDr. Matej Bencúr*, bol slovenský lekár, známejší ako prozaik, dramatik a publicista. Bol **najvýznamnejším predstaviteľom slovenského literárneho realizmu** (*1. vlny - opisného realizmu*), je zakladateľom modernej slovenskej prózy.",
                    "BST": "**Božena Slančíková-Timrava** - predstaviteľka druhej vlny slovenskej realistickej literatúry (kritický realizmus).",
                    "HG": "**Hugolín Gavlovič** - predstaviteľ slovenskej barokovej literatúry"
                }
            }
        }
        ```

        ...tak potom bude hociktorá hodnota daného kľúča prístupná v Markdown súbore poznámok takto:

        ```
        # Literárni autori

        {% for inicialky, autor in k.sjl.autori.items() %}
        - {{ autor }}
        {% endfor %}
        ```
    """

    konstanty = {}

    for json_subor in poznamky_cesta.rglob("*.json"):
        with json_subor.open("r", encoding="utf-8") as s:
            subor_konstanty = json.load(s)
            konstanty = merge(konstanty, subor_konstanty)

    return konstanty



def konvertovat_vsetky_subory(vystupna_cesta: Path, poznamky_cesta: Path) -> None:
    """
        Hlavná funkcia - konvertuje všetky súbory poznámok a Jinja šablón vo výstupnej ceste (`VYSTUPNA_CESTA`).

        Tým pádom je najskôr rozumné prekopírovať všetky potrebné súbory do `VYSTUPNA_CESTA`.
        To sa obyčajne deje v `poznamkovac.__main__.main` prostrednictvom `poznamkovac.sablony.kopirovat_sablony_a_poznamky`
    """

    for subor in vystupna_cesta.rglob("*.*"):
        if subor.stem.startswith('_'):
            subor.unlink()
            continue


        elif subor.suffix == '.md':
            kategorie = ' - '.join(parent.stem for parent in subor.relative_to(vystupna_cesta / poznamky_cesta.stem).parents)
            markdown_text = konvertovat_sablonu(subor.read_text(encoding='utf-8'), k=nacitat_json_konstanty(poznamky_cesta))
            poznamky = vytvorit_poznamky(markdown_text)


            obsah = konvertovat_sablonu(ZAKLAD_POZNAMOK.read_text(encoding='utf-8'),
                title=f"{kategorie} {subor.stem}",
                poznamky=poznamky,
                pojmova_mapa=json.dumps(vytvorit_pojmovu_mapu(markdown_text))
            )


            subor.with_suffix('.html').write_text(obsah, encoding='utf-8')
            subor.unlink()


        elif subor.suffix == '.html':
            sablona = JINJA_ENV.from_string(subor.read_text(encoding='utf-8'))
            subor.write_text(sablona.render(), encoding='utf-8')

