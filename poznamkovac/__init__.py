import typing as t

import json

from pathlib import Path


KORENOVA_CESTA = Path(__file__).parent.absolute()
"""Koreňová cesta k zdrojovému kódu Poznámkovača"""

SABLONY_CESTA = KORENOVA_CESTA / "sablony"
"""Cesta ku Jinja2 šablónam"""

POZNAMKY_CESTA = KORENOVA_CESTA.parent / "poznamky"
"""Cesta k priečinku s poznámkami"""

VYSTUPNA_CESTA = KORENOVA_CESTA.parent / "site"
"""Výstupná cesta, t. j. kde budú umiestnené konvertované poznámky, HTML a statické súbory."""


from poznamkovac.konvertor import nacitat_json_konstanty, vytvorit_poznamky
from poznamkovac.sablony import ZAKLAD_POZNAMOK, konvertovat_sablonu
from poznamkovac.pojmova_mapa import vytvorit_pojmovu_mapu



def konvertovat_vsetky_subory(vystupna_cesta: Path, poznamky_cesta: Path) -> None:
    """
        Hlavná funkcia - konvertuje všetky súbory poznámok a Jinja šablón vo výstupnej ceste (`VYSTUPNA_CESTA`).

        Najskôr je potrebné prekopírovať všetky súbory do `VYSTUPNA_CESTA`.
        To sa zvyčajne deje v `poznamkovac.__main__:main` prostredníctvom `poznamkovac.sablony:kopirovat_sablony_a_poznamky`
    """

    konstanty = nacitat_json_konstanty(poznamky_cesta)
    zoznam_poznamok: dict[str, dict[str, t.Any]] = dict()


    for subor in vystupna_cesta.rglob("*.*"):
        if subor.suffix == '.md':
            # Markdown
            kategorie = ' - '.join(parent.stem for parent in subor.relative_to(vystupna_cesta).parents)
            markdown_text = konvertovat_sablonu(subor.read_text(encoding='utf-8'), k=konstanty)
            poznamky, metadata = vytvorit_poznamky(markdown_text)


            obsah = konvertovat_sablonu(ZAKLAD_POZNAMOK.read_text(encoding='utf-8'),
                titulok=f"{kategorie} {subor.stem}",
                poznamky=poznamky,
                metadata=metadata,
                pojmova_mapa=json.dumps(vytvorit_pojmovu_mapu(markdown_text)) if metadata.get("mapa", ["áno"])[0].lower() != "nie" else None
            )


            subor.with_suffix('.html').write_text(obsah, encoding='utf-8')
            subor.unlink()


        else:
            if subor.stem.startswith('_'):
                continue

            # Ostatné súbory
            obsah = subor.read_text(encoding='utf-8')

            subor.write_text(konvertovat_sablonu(obsah), encoding='utf-8')
            continue


        # Vytvoriť zoznam poznámok z metadát:
        kategoria = metadata.get("kategoria", [subor.parent.stem])[0]
        zoznam_poznamok[kategoria] = {
            "nazov": metadata.get("nazov", [subor.stem])[0],
            "autori": metadata.get("autori", []),
            "popis": metadata.get("popis", [None])[0]
        }


    # Vykresliť zoznam pozámok:
    obsah = (vystupna_cesta / '_zoznam.html').read_text(encoding='utf-8')
    (vystupna_cesta / 'index.html').write_text(konvertovat_sablonu(obsah, zoznam=zoznam_poznamok), encoding='utf-8')


    # Vyčistiť súbory, ktorých mená začínajú s podtržníkom:
    for subor in vystupna_cesta.rglob("*.*"):
        if subor.stem.startswith('_'):
            subor.unlink()
            continue
