# MtG-Proxies

Create a high quality printable PDF from your decklist or a list of cards you want to proxy.

![alt text](examples/decklist.png)

## Features

* **High resolution prints**  
In contrast to online tools that provide this service (e.g. [MTG Press](http://www.mtgpress.net/)), this project creates the PDF file locally.
This allows to use highest resolution Scryfall scans to create a large, high-dpi PDF file without regard for bandwidth limitations. For example, the generated PDF for a complete Commander decklist has a size of about 140MB.

* **Up-to-date card scans**  
By directly utilizing the Scryfall API, all the latest sets are automatically availble as soon as they're available on Scryfall (which is usually incredibly fast). To not overrun Scryfall with requests, this project makes use of [Scryfall bulk data](https://scryfall.com/docs/api/bulk-data) to reduce API calls as much as possible. As requested by Scryfall, a small delay of 100ms is added between requests. However, as most work is done with a local copy of the bulk data, this is hardly noticeable.

* **Sanity checks and recommender engine**  
`mtg-proxies` warns you if you attempt to print a low-resolution scan and is able to offer alternatives.
The convert tool can automatically selects the best print for each card in a decklist with high accuracy, eliminating the need to manually select good prints.

## Usage

1. Clone or download this repo.

```bash
git clone https://github.com/DiddiZ/mtg-proxies.git
```

2. Install requirements. Requires at least [Python 3.7](https://www.python.org/downloads/).

```bash
python -m pip install --user -U -r requirements.txt
```

3. Prepare your decklist in MtG Arena format.

```txt
COUNT FULL_NAME (SET) COLLECTOR_NUMBER
```

E.g.:

```txt
1 Alela, Artful Provocateur (ELD) 324
1 Korvold, Fae-Cursed King (ELD) 329
1 Liliana, Dreadhorde General (WAR) 97
1 Murderous Rider // Swift End (ELD) 287
```

Or use the `convert.py` tool to convert a plain decklist to Arena format:

```bash
python convert.py examples/decklist_text.txt examples/decklist.txt
```

4. Create a PDF file.

```bash
python print.py examples/decklist.txt decklist.pdf
```

## Help

### print

```txt
python print.py [-h] [--dpi DPI] decklist outfile

Prepare a decklist for printing.

positional arguments:
  decklist              a decklist in MtG Arena format
  outfile               output file. Supports pdf, png and jpg.

optional arguments:
  -h, --help            show this help message and exit
  --dpi DPI             dpi of output file
  --paper PAPER         paper size of output
  --border_crop PIXELS  How much to crop inner borders of printed cards
```

### convert

```txt
usage: python convert.py [-h] decklist outfile

Convert a decklist from text format to arena format.

positional arguments:
  decklist    a decklist in text format
  outfile     output file

optional arguments:
  -h, --help  show this help message and exit
```

## ToDo

* Crop marks

## Acknowledgements

* [MTG Press](http://www.mtgpress.net/) for being a very handy online tool, which inspired this project.
* [Scryfall](https://scryfall.com/) for their [excellent API](https://scryfall.com/docs/api).
