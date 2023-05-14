import shutil

from jinja2 import Environment, FileSystemLoader, DebugUndefined
from pathlib import Path

from poznamkovac import SABLONY_CESTA


JINJA_ENV = Environment(loader=FileSystemLoader(SABLONY_CESTA), undefined=DebugUndefined)
ZAKLAD_POZNAMOK = SABLONY_CESTA / '_poznamky.html'



def kopirovat_sablony_a_poznamky(sablony_cesta: Path, poznamky_cesta: Path, vystupna_cesta: Path) -> None:
    """
        Zkopíruje všetky súbory z `sablony_cesta` a `poznamky_cesta` do `vystupna_cesta`.

        Linux ekvivalent (netestované, iba pre ilustráciu):

        ```bash
        cp sablony_cesta/**/* vystupna_cesta/ -R
        cp poznamky_cesta vystupna_cesta/ -R
        ```
    """

    shutil.copytree(sablony_cesta, vystupna_cesta)
    shutil.copytree(poznamky_cesta, vystupna_cesta / poznamky_cesta.stem)



def konvertovat_sablonu(text: str, *args, **kwargs) -> str:
    """
        Vykreslí Jinja2 šablónu.

        `*args` a `**kwargs` budú použité v `Template.render(*args, **kwargs)`
        (sú to kontexty pre premenné v Jinja šablónach).
    """

    sablona = JINJA_ENV.from_string(text)

    return sablona.render(*args, **kwargs)
