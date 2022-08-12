# **PLEASE NOTE**:
I'm not a developer (not anymore). I don't work with backend OR frontend development. I studied and worked as a developer a couple years ago, so I can find and develop what I need but not necessarily using the best practices.

This is an adapted project forked from original and amazing project [Diddiz | mtg-proxies](https://github.com/DiddiZ/mtg-proxies) and from [andrewgioia - mana](https://github.com/andrewgioia/mana). This adaptation wouldn't be possible without their projects.

I know the code and the CSS keeps getting uglier, but I'm happy and this prints what I need so... let's go!!! 

I will fix it eventually... trust me
![winking.gif](https://giphy.com/gifs/disneyplus-disney-wandavision-wanda-vision-6ra84Uso2hoir3YCgb)

# Just... Why?

You know... Magic ain't cheap. 

Third World Countries always struggled with MTG Cards and products. 

The first time I proxied a colored EDH deck it costed me around 25 Dollars and the quality was trash. I wanted to print high quality, minimalist (text only) proxies at home, so I adapted the project for my needs. I don't have to wait 1-2 weeks for a card to be delivered and I don't have to spend 300 dollars in a deck I don't know if I will like (Like I almost did with Atraxa super friends or Slivers).

**WE NOW SUPPORT:**
- Transform cards like [Rowan, Scholar of Sparks // Will, Scholar of Frost](https://scryfall.com/card/stx/A-156/a-rowan-scholar-of-sparks-a-will-scholar-of-frost)
- Card with special icons in the name like [Rowan, Scholar of Sparks // Will, Scholar of Frost](https://scryfall.com/card/stx/A-156/a-rowan-scholar-of-sparks-a-will-scholar-of-frost) and [Growing Rites of Itlimoc](https://scryfall.com/card/xln/191/growing-rites-of-itlimoc-itlimoc-cradle-of-the-sun)
- Color Indicator like [Aberrant Researcher // Perfected Form ](https://scryfall.com/card/soi/49/aberrant-researcher-perfected-form). Please be aware that an empty circle wouldn't be a great representation, so instead of colored circles the color indicator is the MANA SYMBOL instead. Check the card from [Nicol Bolas, the Ravager // Nicol Bolas, the Arisen](https://scryfall.com/card/m19/218/nicol-bolas-the-ravager-nicol-bolas-the-arisen?utm_source=mw_MTGWiki)
![bolas_color_indicator.jpeg](https://github.com/gbartholomeu/mtg-proxies/blob/master/SAMPLES/generated_1.png)
- SPLIT CARDS like [Fire // Ice](https://scryfall.com/card/mh2/290/fire-ice) and [Down // Dirty](https://scryfall.com/card/dgm/126/down-dirty)

Note: There is an issue with [Growing Rites of Itlimoc](https://scryfall.com/card/xln/191/growing-rites-of-itlimoc-itlimoc-cradle-of-the-sun). The API doesn't not contain the metadata used for adding the icon. I already reached Scryfall to check the reason. All other cards worked fine.

Note 2: Split cards have only one design, the rotated version like [Fire // Ice](https://scryfall.com/card/mh2/290/fire-ice). I was lazy...

The transform cards tested had a variety of special symbols like: 
- Day/Night: [Aberrant Researcher // Perfected Form ](https://scryfall.com/card/soi/49/aberrant-researcher-perfected-form)
- Enchantment/Land: [Arguel's Blood Fast // Temple of Aclazotz](https://scryfall.com/card/xln/90/arguels-blood-fast-temple-of-aclazotz)
- Moon/Emrakul: [Cryptolith Fragment // Aurora of Emrakul ](https://scryfall.com/card/emn/193/cryptolith-fragment-aurora-of-emrakul)
- Sparck/Ignite: [Nicol Bolas, the Ravager // Nicol Bolas, the Arisen](https://scryfall.com/card/m19/218/nicol-bolas-the-ravager-nicol-bolas-the-arisen)
- Modal Double Face Cards: [Alrund, God of the Cosmos // Hakka, Whispering Raven](https://scryfall.com/card/khm/40/alrund-god-of-the-cosmos-hakka-whispering-raven?back)
- Lessons: [Academic Probation](https://scryfall.com/card/stx/7/academic-probation)

**THIS VERSION DOES NOT SUPPORT (YET)**
- Tokens like [Saproling](https://scryfall.com/card/tddj/1/saproling);
- Sagas like [Urza's Saga](https://scryfall.com/card/mh2/259/urzas-saga);
- Adventures like [Murderous Rider // Swift End](https://scryfall.com/card/eld/97/murderous-rider-swift-end);
- Cards with huge texts like [Ob Nixilis, the Adversary](https://scryfall.com/card/snc/206/ob-nixilis-the-adversary) and [Jaya, Fiery Negotiator](https://scryfall.com/card/dmu/133/jaya-fiery-negotiator)
- Flip cards like [Bushi Tenderfoot //  Kenzo the Hardhearted1](https://scryfall.com/card/chk/2/bushi-tenderfoot-kenzo-the-hardhearted)

Note: I have not tested this service with:
- Silver-bordered cards;
- Dungeons;
- New Kamigawa Saga icon;
- Any mechanic tracker such as Day/Night;
- Any special card. Is it special and different? I haven't tested it.
- Any token like Treasure, Food, Hint, so far so on.

In case you need to print any of the cards above, I recommend "drawing" the card in the provided template [.html](https://github.com/gbartholomeu/mtg-minimalist-proxies/tree/master/html_card_sample) and css. Use the [generate_proxy.py](https://github.com/gbartholomeu/mtg-minimalist-proxies/blob/master/html_card_sample/generate_proxy.py) file to output the desired image.

## Usage
1. Read [Diddiz | mtg-proxies](https://github.com/DiddiZ/mtg-proxies) original README.md;

2. Clone my repo and run just like the original project. My pipfile has a couple extra packages;

3. To print minimalist proxies use the ```--simple``` argument.

## Template customization

1. Just go read [andrewgioia - mana](https://github.com/andrewgioia/mana) original README.md;
2. I created a new CSS class called ```bw``` (BlackWhite). If you are using the double mana icon (like G/U like in [Gilder Bairn](https://scryfall.com/card/eve/152/gilder-bairn)) it will print a simple non colored version, instead of the colored one.

## Template Testing

I created multiple template samples in [html_card_sample](https://github.com/gbartholomeu/mtg-minimalist-proxies/tree/master/html_card_sample) directory. Just open the desired HTML file in your browser and adjust the CSS/HTML properties as needed. To print the image, adjust the HTML source file and desired outputted image (path + file name) in the [generate_proxy.py](https://github.com/gbartholomeu/mtg-minimalist-proxies/blob/master/html_card_sample/generate_proxy.py) file and run it like any other python file.

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


## License

All card information are copyright Wizards of the Coast ([http://magicthegathering.com](http://magicthegathering.com))


Files are licensed under the MIT License ([http://opensource.org/licenses/mit-license.html](http://opensource.org/licenses/mit-license.html))
!