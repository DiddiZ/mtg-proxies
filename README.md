# **PLEASE NOTE**:
I'm not a developer (not anymore). I don't work with backend OR frontend development. I studied and worked as a developer a couple years ago, so I can find and develop what I need but not necessarily using the best practices.

This is an adapted project forked from original and amazing project [Diddiz | mtg-proxies](https://github.com/DiddiZ/mtg-proxies) and from [andrewgioia - mana](https://github.com/andrewgioia/mana). This adaptation wouldn't be possible without their projects.

# Just... Why?

You know... Magic ain't cheap. 

Third World Countries always struggled with MTG Cards and products. 

The first time I proxied a colored EDH deck it costed me around 25 Dollars and the quality was trash. I wanted to print high quality, minimalist (text only) proxies at home, so I adapted the project for my needs. I don't have to wait 1-2 weeks for a card to be delivered and I don't have to spend 300 dollars in a deck I don't know if I will like (Like I almost did with Atraxa super friends or Slivers).

**THIS VERSION DOES NOT SUPPORT SPLIT CARDS (YET) - Like [Fire // Ice](https://scryfall.com/card/mh2/290/fire-ice)**
**THIS VERSION DOES NOT SUPPORT FLIP CARDS (YET) - Like [Rowan, Scholar of Sparks // Will, Scholar of Frost](https://scryfall.com/card/stx/A-156/a-rowan-scholar-of-sparks-a-will-scholar-of-frost)**

## Usage
1. Read [Diddiz | mtg-proxies](https://github.com/DiddiZ/mtg-proxies) original README.md;

2. Clone my repo and run just like the original project. My pipfile has a couple extra packages;

3. To print minimalist proxies use the ```--simple``` argument.

## Template customization

1. Just go read [andrewgioia - mana](https://github.com/andrewgioia/mana) original README.md;
2. I created a new CSS class called ```bw``` (BlackWhite). If you are using the double mana icon (like G/U like in [Gilder Bairn](https://scryfall.com/card/eve/152/gilder-bairn)) it will print a simple non colored version, instead of the colored one.

## How it works - My customization

1. I use the fetched data to generate an HTML file with the card content;
2. Run a headless Chromium process to render the HTML and screenshot the card image to the temporary folder of your OS.

# Known issues
1. This is Unix/Mac only (for now) due to the path structure I used;
2. CSS has fixed values for font size, font spacing, position, etc. It means it won't properly work with cards with huge texts like [Reyhan, Last of the Abzan](https://scryfall.com/card/cm2/13/reyhan-last-of-the-abzan) and [Arixmethes, Slumbering Isle](https://scryfall.com/card/2xm/189/arixmethes-slumbering-isle) (it breaks the power/thoughness box for Arixmethes);
3. It doesn't support all mana icons for now. I will create the hybrid Phyrexian mana from cards like [Tamiyo, Compleated Sage](https://scryfall.com/card/neo/238/tamiyo-compleated-sage);
4. The system won't replace already generated images. So if you want to generate a new version of the same card (or patched version), you must first delete it before running the software;
5. I tested it a lot and sometimes the chromium process hangs and it freezes the image generation. Just stop the process, clean the cache folder and start over again;
6. The hybrid mana from cards like [Gilder Bairn](https://scryfall.com/card/eve/152/gilder-bairn) prints a square instead of a circle. This is an issue with the ```border-radius``` CSS property. It only happens with the Chromium version used by **pyppeteer**. When I tested directly from the Chromium browser it didn't happen.

### Samples
- Broken cards: ./SAMPLES/brokenCards.pdf
- Ok Cards: ./SAMPLES/okCards.pdf 
- Printed 1: ![printedCard_1.jpeg](https://github.com/gbartholomeu/mtg-proxies/blob/master/SAMPLES/printed_1.jpeg)
- Printed 2: ![printedCard_1.jpeg](https://github.com/gbartholomeu/mtg-proxies/blob/master/SAMPLES/printed_2.jpeg)

## Acknowledgements

- [Diddiz | mtg-proxies](https://github.com/DiddiZ/mtg-proxies)
- [andrewgioia - mana](https://github.com/andrewgioia/mana)
