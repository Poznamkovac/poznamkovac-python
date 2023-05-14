#!/usr/bin/env python3
import shutil

from poznamkovac import VYSTUPNA_CESTA, SABLONY_CESTA, POZNAMKY_CESTA, konvertovat_vsetky_subory
from poznamkovac.sablony import kopirovat_sablony_a_poznamky



def main() -> None:
    """
        Hlavná funkcia, kde sa dejú všetky kúzla 🧙‍♂️ ⚡
    """

    # Ak už existuje `VYSTUPNA_CESTA`, vytvoríme ju nanovo
    # ...kvázi ju "prepíšeme".
    if VYSTUPNA_CESTA.exists():
        shutil.rmtree(VYSTUPNA_CESTA)

    kopirovat_sablony_a_poznamky(SABLONY_CESTA, POZNAMKY_CESTA, VYSTUPNA_CESTA)
    konvertovat_vsetky_subory(VYSTUPNA_CESTA, POZNAMKY_CESTA)

    # Toto chceme vidieť:
    print(f"HTML výstup bol vygenerovaný v `{VYSTUPNA_CESTA}` 👀")



if __name__ == '__main__':
    main()