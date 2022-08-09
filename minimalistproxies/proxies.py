from __future__ import annotations
import os
from mtgproxies.decklists.decklist import Card
from pathlib import Path
from tempfile import gettempdir
import shutil
import re
import asyncio
from pyppeteer import launch
import time

cache = Path(gettempdir()) / "scryfall_cache"
cache.mkdir(parents=True, exist_ok=True)  # Create cache folder
MANA_COST_MAPPING={
    '{W}': 'ms ms-w',
    '{U}': 'ms ms-u',
    '{B}': 'ms ms-b',
    '{R}': 'ms ms-r',
    '{G}': 'ms ms-g',
    '{T}': 'ms ms-tap',
    '{Q}': 'ms ms-untap',
    '{E}': 'ms ms-e',
    '{X}': 'ms ms-x',
    '{Y}': 'ms ms-y',
    '{Z}': 'ms ms-z',
    '{0}': 'ms ms-0',
    '{1}': 'ms ms-1',
    '{2}': 'ms ms-2',
    '{3}': 'ms ms-3',
    '{4}': 'ms ms-4',
    '{5}': 'ms ms-5',
    '{6}': 'ms ms-6',
    '{7}': 'ms ms-7',
    '{8}': 'ms ms-8',
    '{9}': 'ms ms-9',
    '{10}': 'ms ms-10',
    '{11}': 'ms ms-11',
    '{12}': 'ms ms-12',
    '{13}': 'ms ms-13',
    '{14}': 'ms ms-14',
    '{15}': 'ms ms-15',
    '{16}': 'ms ms-16',
    '{17}': 'ms ms-17',
    '{18}': 'ms ms-18',
    '{19}': 'ms ms-19',
    '{20}': 'ms ms-20',
    '{100}': 'ms ms-100',
    '{1000000}': 'ms ms-1000000',
    '{W/U}': 'ms ms-wu ms-cost bw', 
    '{W/B}': 'ms ms-wb ms-cost bw', 
    '{B/R}': 'ms ms-br ms-cost bw', 
    '{B/G}': 'ms ms-bg ms-cost bw', 
    '{U/B}': 'ms ms-ub ms-cost bw', 
    '{U/R}': 'ms ms-ur ms-cost bw', 
    '{R/G}': 'ms ms-rg ms-cost bw', 
    '{R/W}': 'ms ms-rw ms-cost bw', 
    '{G/W}': 'ms ms-gw ms-cost bw', 
    '{G/U}': 'ms ms-gu ms-cost bw', 
    '{W/P}': 'ms ms-wp ms-cost bw', 
    '{U/P}': 'ms ms-up ms-cost bw', 
    '{B/P}': 'ms ms-bp ms-cost bw', 
    '{R/P}': 'ms ms-rp ms-cost bw', 
    '{G/P}': 'ms ms-gp ms-cost bw',
    '{HW}': 'ms ms-w ms-half',
    '{HR}': 'ms ms-r ms-half',
    '{S}': 'ms ms-s',
    '{C}': 'ms ms-c'
}

PLANESWALKER_LOYALTY_MAPPING={
    'commom_css': 'ms',
    'start_loyalty': 'ms-5x ms-loyalty-start',
    'up_loyalty': 'ms-loyalty-up',
    'down_loyalty': 'ms-loyalty-down',
    'loyalty_amount': 'ms-2x ms-loyalty-'
}


def get_minimalist_proxies(card: Card) -> list[str]:
    file_name = f"minimalist_{card['name'].replace(' ','_').replace('//', '_')}.png"
    prepate_html_css(card)
    loop =  asyncio.get_event_loop()
    call = convert_html_to_png(f'{cache}/html_temp/html_template.html', str(cache / file_name))
    loop.run_until_complete(call)
    return str(cache / file_name)


def prepate_html_css(card: Card):
    src = f'{os.getcwd()}/minimalistproxies/html'
    dest = f'{cache}/html_temp'
    
    if os.path.exists(dest):
        shutil.rmtree(dest)

    shutil.copytree(src, dest, copy_function = shutil.copy)
    html_file = f'{dest}/html_template.html'
    css_file = f'{dest}/css/main.css'

    if 'creature' in card['type_line'].lower():
        setupCreatureCard(card, html_file, css_file)
    if 'planeswalker' in card['type_line'].lower():
        setupPlaneswalkerCard(card, html_file, css_file)
    else:
        setupOtherCard(card, html_file, css_file)

def setupCreatureCard(card, html_file, css_file):
    if card['layout'].lower() in ['split', 'adventure', 'saga', 'token']:
        card_template = f'black_empty.png'
        css_data = ''

        with open(css_file, 'rt') as input_file:
            data = input_file.read()
            css_data = data.replace('##REPLACE_BACKGROUND_IMAGE', card_template)

        with open(css_file, 'wt') as output_file:
            data = output_file.write(css_data)
    else:
        legend = 'legendary' if 'legendary' in card['type_line'].lower() else ''
        card_template = f'black_creature{legend}.png'
        css_data = ''

        with open(css_file, 'rt') as input_file:
            data = input_file.read()
            css_data = data.replace('##REPLACE_BACKGROUND_IMAGE', card_template)

        with open(css_file, 'wt') as output_file:
            data = output_file.write(css_data)

        with open(html_file, 'rt') as input_file:
            data = input_file.read()
            data = data.replace('<!--##REPLACE_CARD_NAME-->', card['name'])
            data = data.replace('<!--##REPLACE_CARD_TYPE-->', card['type_line'])

            cost = re.findall('\{[0-9A-Z\/]+\}', card['mana_cost'])
            mana_icons_html = ''
            
            #Mana Icons - Card cost
            for mana_symbol in cost:
                if mana_symbol in MANA_COST_MAPPING:
                    mana_icons_html += f'<i class="{MANA_COST_MAPPING[mana_symbol]}" id="mana-icon"></i>'
                else:
                    mana_icons_html += f'<i class="{mana_symbol}" id="mana-icon"></i>'

            data = data.replace('<!--##REPLACE_CARD_COST-->', mana_icons_html)

            unfiltered_card_text = card['oracle_text']
            card_text = ''

            for icon, text in MANA_COST_MAPPING.items(): 
                if icon in unfiltered_card_text:
                    unfiltered_card_text = unfiltered_card_text.replace(icon, f'<span class="{text}"></span>')


            for line in unfiltered_card_text.splitlines():
                card_text += f'<p class="description">{line}</p>'

            data = data.replace('<!--##REPLACE_CARD_TEXT-->', card_text)
            data = data.replace('<!--##REPLACE_CARD_POWER-->', f'<h1 class="power-thoughness">{card["power"]} / {card["toughness"]}</h1>')

            html_data = data

        with open(html_file, 'wt') as output_file:
            data = output_file.write(html_data)


def setupPlaneswalkerCard(card, html_file, css_file):
    card_template = f'black_legendary.png'
    css_data = ''

    with open(css_file, 'rt') as input_file:
        data = input_file.read()
        css_data = data.replace('##REPLACE_BACKGROUND_IMAGE', card_template)

    with open(css_file, 'wt') as output_file:
        data = output_file.write(css_data)

    with open(html_file, 'rt') as input_file:
        data = input_file.read()
        data = data.replace('<!--##REPLACE_CARD_NAME-->', card['name'])
        data = data.replace('<!--##REPLACE_CARD_TYPE-->', card['type_line'])

        cost = re.findall('\{[0-9A-Z\/]+\}', card['mana_cost'])
        mana_icons_html = ''

        #Mana Icons - Card cost
        for mana_symbol in cost:
            if mana_symbol in MANA_COST_MAPPING:
                mana_icons_html += f'<i class="{MANA_COST_MAPPING[mana_symbol]}" id="mana-icon"></i>'
            else:
                mana_icons_html += f'<i class="{mana_symbol}" id="mana-icon"></i>'

        data = data.replace('<!--##REPLACE_CARD_COST-->', mana_icons_html)

        raw_card_text = card['oracle_text']
        unfiltered_text = ''
        card_text = ''

        for line in raw_card_text.splitlines():
            loyalty = re.findall('^([−+])([0-9]{1,2})?(.+)', line)
        
            if len(loyalty) == 0:
                card_text += f'<p class="description">{line}</p>'
            else:
                css_loyalty = PLANESWALKER_LOYALTY_MAPPING['commom_css']
                if '+' == loyalty[0][0]:
                    css_loyalty += f' {PLANESWALKER_LOYALTY_MAPPING["up_loyalty"]}'
                else:
                    css_loyalty += f' {PLANESWALKER_LOYALTY_MAPPING["down_loyalty"]}'
                
                css_loyalty += f' {PLANESWALKER_LOYALTY_MAPPING["loyalty_amount"]}{loyalty[0][1]}'
                css_loyalty = f'<span class="{css_loyalty}"></span>'

                card_text += f'<p class="description">{css_loyalty}{loyalty[0][2]}</p>'

        unfiltered_text = card_text

        for icon, text in MANA_COST_MAPPING.items(): 
            if icon in unfiltered_text:
                card_text = unfiltered_text.replace(icon, f'<span class="{text}"></span>')

        data = data.replace('<!--##REPLACE_CARD_TEXT-->', card_text)
        data = data.replace('<!--##REPLACE_PLANESWALKER_LOYALTY-->', f'<div class="{PLANESWALKER_LOYALTY_MAPPING["commom_css"]} {PLANESWALKER_LOYALTY_MAPPING["start_loyalty"]} {PLANESWALKER_LOYALTY_MAPPING["loyalty_amount"]}{card["loyalty"]}"></div>')

        html_data = data

    with open(html_file, 'wt') as output_file:
        data = output_file.write(html_data)

def setupOtherCard(card, html_file, css_file):
    if card['layout'].lower() in ['split', 'adventure', 'saga', 'token']:
        card_template = f'black_empty.png'
        css_data = ''

        with open(css_file, 'rt') as input_file:
            data = input_file.read()
            css_data = data.replace('##REPLACE_BACKGROUND_IMAGE', card_template)

        with open(css_file, 'wt') as output_file:
            data = output_file.write(css_data)
    else:
        legend = 'legendary' if 'legendary' in card['type_line'].lower() else ''
        card_template = f'black_{legend}.png'
        css_data = ''

        with open(css_file, 'rt') as input_file:
            data = input_file.read()
            css_data = data.replace('##REPLACE_BACKGROUND_IMAGE', card_template)

        with open(css_file, 'wt') as output_file:
            data = output_file.write(css_data)

        with open(html_file, 'rt') as input_file:
            data = input_file.read()
            data = data.replace('<!--##REPLACE_CARD_NAME-->', card['name'])
            data = data.replace('<!--##REPLACE_CARD_TYPE-->', card['type_line'])

            cost = re.findall('\{[0-9A-Z\/]+\}', card['mana_cost'])
            mana_icons_html = ''
            
            #Mana Icons - Card cost
            for mana_symbol in cost:
                if mana_symbol in MANA_COST_MAPPING:
                    mana_icons_html += f'<i class="{MANA_COST_MAPPING[mana_symbol]}" id="mana-icon"></i>'
                else:
                    mana_icons_html += f'<i class="{mana_symbol}" id="mana-icon"></i>'

            data = data.replace('<!--##REPLACE_CARD_COST-->', mana_icons_html)

            unfiltered_card_text = card['oracle_text']
            card_text = ''

            for icon, text in MANA_COST_MAPPING.items(): 
                if icon in unfiltered_card_text:
                    unfiltered_card_text = unfiltered_card_text.replace(icon, f'<span class="{text}"></span>')


            for line in unfiltered_card_text.splitlines():
                card_text += f'<p class="description">{line}</p>'

            data = data.replace('<!--##REPLACE_CARD_TEXT-->', card_text)
            html_data = data

        with open(html_file, 'wt') as output_file:
            data = output_file.write(html_data)
        
async def convert_html_to_png(html_path: str,  file_name:str):
    browser = await launch()
    page = await browser.newPage()
    await page.goto(f'file://{html_path}')
    await page.screenshot({'path': file_name, 'clip':{'x':0,'y':0, 'width': 1540, 'height': 2140} })
    await browser.close()






