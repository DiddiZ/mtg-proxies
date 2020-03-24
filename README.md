# MtG-Proxies

Create a high quality printable PDF from your decklist or a list of cards you want to proxy.

## Usage

1. Clone or download this repo.

```bash
git clone https://github.com/DiddiZ/mtg-proxies.git
```

2. Install requirements.

```bash
python -m pip install --user -U -r requirements.txt
```

2. Prepare your decklist in MtG Arena format.

```txt
COUNT FULL_NAME (SET) COLLECTOR_NUMBER
```

E.g.:

```txt
1 Alela, Artful Provocateur (ELD) 324
1 Korvold, Fae-Cursed King (ELD) 329
1 Liliana, Dreadhorde General (WAR) 97
1 Murderous Rider (ELD) 287
```

3. Create a PDF file.

```bash
python print.py examples/decklist.txt decklist.pdf
```

## Help


```txt
python print.py [-h] [--dpi DPI] decklist outfile

Prepare a decklist for printing.

positional arguments:
  decklist    a decklist in MtG Arena format
  outfile     output file. Supports pdf, png and jpg.

optional arguments:
  -h, --help  show this help message and exit
  --dpi DPI   dpi of output file
```

## Acknowledgements

* [MTG Press](http://www.mtgpress.net/) for being a very handy online tool, which almost exactly does the same as this project.
* [Scryfall](https://scryfall.com/) for their [excellent API](https://scryfall.com/docs/api).
