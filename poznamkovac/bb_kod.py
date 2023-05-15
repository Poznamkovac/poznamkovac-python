import re

from bbcode import Parser


BBKOD_KONVERTOR = Parser(
    # Nechceme cenzurovať HTML ktoré bolo vygenerované `poznamkovac.md`.
    # Toto nastavenie by bolo `True` ak by napr.: bol obsah 100 % vytváraný
    # používateľmi (napr.: na sociálnych sieťach), ale toto nie je ten prípad.
    # 
    # V Poznámkovači sa všetko deje prostredníctvom Markdown súborov, ktorých
    # obsah prechádza manuálnou kontrolou, teda nepotrebujeme escapovať HTML:
    escape_html=False,

    # Toto za nás urobí `poznamkovac.md`:
    replace_links=False,

    # Predvolené nastavenie je `<br />`, to by avšak
    # zamávalo s Markdown nastaveniami, a `\n` by boli zdvojené:
    newline='\n',

    # Hranaté zátvorky sa už používajú v kontexte odkazov na iné stránky,
    # takže markdownlint s tým má v určitých situáciách problém:
    tag_opener=r'{', tag_closer=r'}',
)

# Z nejakého dôvodu sa aj napriek `escape_html == False`
# cenzurujú obsahy rôznych tagov, preto manuálne monkey-patchneme
# `REPLACE_ESCAPE` zoznam znakov z `bbcode.Parser`.
BBKOD_KONVERTOR.REPLACE_ESCAPE = tuple()


def _zvyraznovac(_, hodnota: str, moznosti: dict[str, str], *__):
    """
        BBCode tag pre `[z]` (zvýrazňovač).

        Použitie:

        ```markdown
        Toto je [z=lime]limetkovo zvýraznený text[/z] (t. j.: zelený).
        ```
    """

    # Ak je farba v možnostiach (atribútach):
    if "z" in moznosti:
        farba = moznosti["z"].strip()

    # Ak je viacej možností, vyberie sa iba jedna:
    elif moznosti:
        farba = list(moznosti.keys())[0].strip()

    # Ak nie je nič na vybratie, vyberie sa predvolená žltá farba:
    else:
        farba = "yellow"

    # Podporuje CSS mená farieb a HEX kódy:
    match = re.match(r"^([a-z]+)|^(#[a-f0-9]{3,6})", farba, re.I)
    farba = match.group() if match else "inherit"

    return f'<span class="zvyraznovac" style="--farba: {farba};">{hodnota}</span>'

BBKOD_KONVERTOR.add_formatter("z", _zvyraznovac)
BBKOD_KONVERTOR.add_simple_formatter("uceleny_obsah", '<div class="uceleny-obsah">%(value)s</div>')



def konvertovat_bbkod(text: str) -> str:
    """
        Konvertuje text na [BB kód](https://bbcode.readthedocs.io/en/latest/tags.html).
    """

    return BBKOD_KONVERTOR.format(text)
