from __future__ import annotations
import os
from mtgproxies.decklists.decklist import Card
from pathlib import Path
from tempfile import gettempdir
import shutil
import re
import asyncio
from pyppeteer import launch

cache = Path(gettempdir()) / "scryfall_cache"
cache.mkdir(parents=True, exist_ok=True)  # Create cache folder
MANA_COST_MAPPING = {
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

PLANESWALKER_LOYALTY_MAPPING = {
    'commom_css': 'ms',
    'start_loyalty': 'ms-5x ms-loyalty-start',
    'up_loyalty': 'ms-loyalty-up',
    'down_loyalty': 'ms-loyalty-down',
    'loyalty_amount': 'ms-2x ms-loyalty-'
}

MODAL_ICONS_MAPPING = {
    'day': 'ms ms-dfc-day',
    'night': 'ms ms-dfc-night',
    'sparck': 'ms ms-dfc-spark',
    'ignite': 'ms ms-dfc-ignite',
    'enchantment': 'ms ms-dfc-enchantment',
    'land': 'ms ms-land',
    'moon': 'ms ms-dfc-moon',
    'emrakul': 'ms ms-dfc-emrakul',
    'modal_front': 'ms ms-dfc-modal-face',
    'modal_back': 'ms ms-dfc-modal-back',
    'lesson': 'ms ms-dfc-lesson'
}


def get_minimalist_proxies(card: Card, opposite_card: Card = [], full_card: Card = []) -> list[str]:
    file_name = 'minimalist_'
    if card.__contains__('set'):     
        file_name += f"{card['name'].replace(' ','_').replace('//', '_')}-{card['set']}"
    elif full_card and full_card.__contains__('set'):
        file_name += f"{card['name'].replace(' ','_').replace('//', '_')}-{full_card['set']}"
    file_name += '.png'

    prepare_html_css(card, opposite_card, full_card)
    loop = asyncio.get_event_loop()
    call = convert_html_to_png(f'{cache}/html_temp_{card["name"]}/html_template.html', str(cache / file_name))
    loop.run_until_complete(call)

    return str(cache / file_name)


def prepare_html_css(card: Card, opposite_card: Card, full_card: Card):
    html_file, css_file = prepare_files(card["name"])

    setup_card([card, opposite_card, full_card], html_file, css_file)


def prepare_files(card_name: str):
    # I'll keep this card_name target until I finish developing most cards layouts
    src = f'{os.getcwd()}/minimalistproxies/html'
    dest = f'{cache}/html_temp_{card_name}'

    if os.path.exists(dest):
        shutil.rmtree(dest)

    shutil.copytree(src, dest, copy_function=shutil.copy)
    html_file = f'{dest}/html_template.html'
    css_file = f'{dest}/css/main.css'

    return html_file, css_file


def setup_card(cards: list[Card], html_file, css_file):
    template = get_card_template(cards)
    fill_css_file(template, css_file)
    fill_html_file(cards, html_file)


def get_card_template(cards: list[Card]) -> str:
    template = 'black_'

    if cards[0].__contains__('layout') and cards[0]['layout'].lower() in ['adventure', 'saga', 'flip']:
        template += 'empty'
    elif cards[2] and cards[2].__contains__('layout') and cards[2]['layout'].lower() == 'split':
        template += 'split'
    else:
        if "creature" in cards[0]['type_line'].lower():
            template += 'creature'

        if 'legendary' in cards[0]['type_line'].lower():
            template += 'legendary'

    template += ".png"

    return template


def fill_css_file(template: str, css_file):
    with open(css_file, 'rt') as input_file:
        data = input_file.read()
        css_data = data.replace('##REPLACE_BACKGROUND_IMAGE', template)

    with open(css_file, 'wt') as output_file:
        data = output_file.write(css_data)


def fill_html_file(cards: list[Card], html_file):
    upper_part = fill_upper_part_html(cards)
    middle_part = fill_middle_part_html(cards)
    bottom_part = fill_bottom_part_html(cards)

    with open(html_file, 'rt') as input_file:
        data = input_file.read()
        data = data.replace('<!--##REPLACE_UPPER_PART-->', upper_part)
        data = data.replace('<!--##REPLACE_MIDDLE_PART-->', middle_part)
        data = data.replace('<!--##REPLACE_BOTTOM_PART-->', bottom_part)

        html_data = data

    with open(html_file, 'wt') as output_file:
        data = output_file.write(html_data)


def fill_upper_part_html(cards: list[Card]) -> str:
    upper_html = ''

    if cards[2] and cards[2].__contains__('card_faces') and cards[2]['layout'].lower() in ['split']:  #['split','flip']
        for face in range(2):
            card_name = replace_card_name_html([cards[2]["card_faces"][face],[]])
            card_mana_cost= replace_mana_html(cards[2]['card_faces'][face]['mana_cost']) 
            upper_html  += f"""
                                <div class="frame-header split{face+1}">
                                        <h1 class="name">{card_name}</h1>
                                        <div class="mana-frame">
                                            {card_mana_cost}
                                        </div>
                                </div>
                                """

    else: 
        card_name = replace_card_name_html(cards)
        card_mana_cost= replace_mana_html(cards[0]['mana_cost']) 
        upper_html  = f"""
                            <div class="frame-header">
                                    <h1 class="name">{card_name}</h1>
                                    <div class="mana-frame">
                                        {card_mana_cost}
                                    </div>
                            </div>
                            """

    return upper_html

def fill_middle_part_html(cards: list[Card]) -> str:
    middle_html = ''
    
    if cards[2] and cards[2].__contains__('card_faces') and cards[2]['layout'].lower() in ['split']:  #['split','flip']
        for face in range(2):
            card_type = replace_color_indicator(cards[2]["card_faces"][face])
            middle_html  += f"""
                                <div class="frame-type-line split{face+1}">
                                    <h1 class="type">{card_type}</h1>
                                </div>
                                """

    else: 
        card_type = replace_color_indicator(cards[0])
        middle_html  = f"""
                            <div class="frame-type-line">
                                <h1 class="type">{card_type}</h1>
                            </div>
                            """

    return middle_html

def fill_bottom_part_html(cards: list[Card]) -> str:
    bottom_html = ''
    if cards[2] and cards[2].__contains__('card_faces') and cards[2]['layout'].lower() in ['split']:  #['split','flip']
        for face in range(2):
            card_text = replace_text_symbols(cards[2]["card_faces"][face]['oracle_text'])
            card_power_toughness = replace_card_power_toughness(cards[2]["card_faces"][face])
            card_back = replace_back_card_info(cards)
            card_loyalty = replace_planeswalker_loyalty(cards[2]["card_faces"][face])

            if card_text:
                bottom_html += f"""
                                <div class="frame-text-box split{face+1}">
                                    {card_text}
                                </div>
                                """ 
            if card_power_toughness:
                bottom_html +=  f"""
                                <div class="frame-power-toughness split{face+1}">
                                    {card_power_toughness}
                                </div>
                                """ 
            if card_back:
                bottom_html +=  f"{card_back}" 
            
            if card_loyalty:
                bottom_html +=  f"""
                                <div class="frame-loyalty split{face+1}">
                                    {card_loyalty}
                                </div>
                                """
    else:
        card_text = replace_text_symbols(cards[0]['oracle_text'])
        card_power_toughness = replace_card_power_toughness(cards[0])
        card_back = replace_back_card_info(cards)
        card_loyalty = replace_planeswalker_loyalty(cards[0])

        if card_text:
            bottom_html += f"""
                            <div class="frame-text-box">
                                {card_text}
                            </div>
                            """ 
        if card_power_toughness:
            bottom_html +=  f"""
                            <div class="frame-power-toughness">
                                {card_power_toughness}
                            </div>
                            """ 
        if card_back:
            bottom_html +=  f"{card_back}" 
        
        if card_loyalty:
            bottom_html +=  f"""
                            <div class="frame-loyalty">
                                {card_loyalty}
                            </div>
                            """

    return bottom_html

def replace_card_name_html(cards: list[Card]) -> str:
    card_name = cards[0]['name']

    if cards[1] and cards[2]['layout'].lower() in ['modal_dfc', 'transform']:
        split_original = cards[2]['name'].replace('/', '@').split('@')

        if cards[2].__contains__('frame_effects') and 'originpwdfc' in cards[2]['frame_effects']:
            if card_name.strip() == split_original[0].strip():
                card_name = f'<span class="{MODAL_ICONS_MAPPING["sparck"]}"></span> {card_name}'
            else:
                card_name = f'<span class="{MODAL_ICONS_MAPPING["ignite"]}"></span> {card_name}'
        elif cards[2].__contains__('frame_effects') and 'sunmoondfc' in cards[2]['frame_effects']:
            if card_name.strip() == split_original[0].strip():
                card_name = f'<span class="{MODAL_ICONS_MAPPING["day"]}"></span> {card_name}'
            else:
                card_name = f'<span class="{MODAL_ICONS_MAPPING["night"]}"></span> {card_name}'
        elif cards[2].__contains__('frame_effects') and 'compasslanddfc' in cards[2]['frame_effects']:
            if card_name.strip() == split_original[0].strip():
                card_name = f'<span class="{MODAL_ICONS_MAPPING["enchantment"]}"></span> {card_name}'
            else:
                card_name = f'<span class="{MODAL_ICONS_MAPPING["land"]}"></span> {card_name}'
        elif cards[2].__contains__('frame_effects') and 'mooneldrazidfc' in cards[2]['frame_effects']:
            if card_name.strip() == split_original[0].strip():
                card_name = f'<span class="{MODAL_ICONS_MAPPING["moon"]}"></span> {card_name}'
            else:
                card_name = f'<span class="{MODAL_ICONS_MAPPING["emrakul"]}"></span> {card_name}'
        elif 'modal_dfc' == cards[2]['layout']:
            if card_name.strip() == split_original[0].strip():
                card_name = f'<span class="{MODAL_ICONS_MAPPING["modal_front"]}"></span> {card_name}'
            else:
                card_name = f'<span class="{MODAL_ICONS_MAPPING["modal_back"]}"></span> {card_name}'

    elif cards[0].__contains__('frame_effects') and 'lesson' in cards[0]['frame_effects']:
        card_name = f'<span class="{MODAL_ICONS_MAPPING["lesson"]}"></span> {card_name}'

    return card_name


def replace_color_indicator(card: Card) -> str:
    card_type_text = card['type_line']     

    if card.__contains__('color_indicator'):
        filtered_mana = ''
        for color in card['color_indicator']:
            filtered_mana += f'{{{color}}}'
        replaced_mana = replace_mana_html(filtered_mana, False)
        card_type_text = f'{replaced_mana} - {card_type_text}'

    return card_type_text


def replace_mana_html(mana: str, replace_css_id: bool = True) -> str:
    css_id = f'id="mana-icon"' if replace_css_id else ''
    replaced_text = mana

    for icon, text in MANA_COST_MAPPING.items():
        if icon in mana:
            replaced_text = replaced_text.replace(icon, f'<span class="{text}" {css_id}></span>')

    return replaced_text


def replace_loyalty_counter(text: str) -> str:
    card_text = ''

    for line in text.splitlines():
        loyalty = re.findall('^([−+])([0-9]{1,2})?(.+)', line)

        if len(loyalty) == 0:
            card_text += f'<p>{line}</p>\n'
        else:
            css_loyalty = PLANESWALKER_LOYALTY_MAPPING['commom_css']
            if '+' == loyalty[0][0]:
                css_loyalty += f' {PLANESWALKER_LOYALTY_MAPPING["up_loyalty"]}'
            else:
                css_loyalty += f' {PLANESWALKER_LOYALTY_MAPPING["down_loyalty"]}'

            css_loyalty += f' {PLANESWALKER_LOYALTY_MAPPING["loyalty_amount"]}{loyalty[0][1]}'
            css_loyalty = f'<span class="{css_loyalty}"></span>'

            card_text += f'<p>{css_loyalty}{loyalty[0][2]}</p>\n'

    return card_text


def replace_text_symbols(text: str) -> str:
    # card_text = ''
    loyalty_replaced = replace_loyalty_counter(text)
    mana_replaced = replace_mana_html(loyalty_replaced, False)
    # for line in mana_replaced.splitlines():
    #     card_text += f'<p>{line}</p>\n'

    return mana_replaced


def replace_card_power_toughness(card: Card) -> str:
    card_power_toughness = ''
    if card.__contains__('power'):
        card_power_toughness = f'<h1 class="power-thoughness">{card["power"]} / {card["toughness"]}</h1>'

    return card_power_toughness


def replace_back_card_info(cards: list[Card]) -> str:
    card_info = ''

    if cards[1] and cards[2]['layout'].lower() in ["modal_dfc"]:
        identifier = cards[1]['type_line'].split(' ')
        back_card_name = identifier[-1]
        back_card_cost = replace_mana_html(cards[1]['mana_cost'], False)
        card_info = f'<div class="frame-opposite-card">\n\t\t<p>{back_card_name}<span class="mana-frame-opposite-card">{back_card_cost}</span>\n</p>\n\t</div>'

    return card_info


def replace_planeswalker_loyalty(card: Card) -> str:
    loyalty_css = ''
    if 'planeswalker' in card['type_line'].lower():
        loyalty_css = f'<div class="{PLANESWALKER_LOYALTY_MAPPING["commom_css"]} {PLANESWALKER_LOYALTY_MAPPING["start_loyalty"]} {PLANESWALKER_LOYALTY_MAPPING["loyalty_amount"]}{card["loyalty"]}"></div>'

    return loyalty_css


async def convert_html_to_png(html_path: str, file_name: str):
    browser = await launch()
    page = await browser.newPage()
    await page.goto(f'file://{html_path}')
    await page.screenshot({'path': file_name, 'clip': {'x': 0, 'y': 0, 'width': 1540, 'height': 2140}})
    await browser.close()
