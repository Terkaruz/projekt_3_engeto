# projekt_3_engeto

Třetí projekt na Python Akademií od Engeta.

## Popis projektu

Tento projekt slouží k extrahování výsledků parlamentních voleb v roce 2017. Odkaz k prohlédnutí najdete [zde](https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ).

## Instalace knihoven

Knihovny, které jsou použity v kódu, jsou uložené v souboru `requirements.txt`. Pro instalaci doporučuji použít nové virtuální prostředí a s nainstalovaným manažerem spustit následovně:

```powershell
pip --version                       # overi aktualni verzi manazera
pip install -r requirements.txt     # nainstaluje knihovny
```

## Spuštění projektu

Spuštění souboru `projekt_3.py` v rámci příkazového řádku požaduje dva povinné argumenty.

```powershell
python projekt_3.py <odkaz-uzemniho-celku> <vysledny-csv-soubor>
```

Následně se ze zadaného odkazu stáhnou výsledky a uloží do požadovaného souboru s příponou `.csv`.

## Ukázka projektu

Výsledky hlasování pro okres Kroměříž:

1. argument: `https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=13&xnumnuts=7201`
2. argument: `kromeriz_results.csv`
 
Spuštění programu:

```powershell
python projekt_3.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=13&xnumnuts=7201" "kromeriz_results.csv"
```

Průběh stahování:

```text
VALIDATING INPUTS
[OK]
DOWNLOADING DATA FROM SPECIFIED URL: https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=13&xnumnuts=7201
[OK]
SAVING DATA TO FILE: kromeriz_results.csv
[OK]

TERMINATING projekt_3.py
```

Částečný výstup:

```csv
code;location;registered;envelopes;valid;...
588300;Bařice-Velké Těšany;374;269;268;15;0;1;20;0;20;30;1;1;3;0;0;17;0;9;71;0;1;30;2;0;0;46;1
588326;Bezměrov;426;270;264;20;0;0;21;0;1;21;0;4;2;0;0;22;0;6;86;1;1;25;3;1;0;47;3
...
```