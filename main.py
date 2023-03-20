from urllib.parse import urljoin
from helpers import *


def velosklad_parse(link_for_bike: str) -> dict:
    """
    Функция парсит сайт https://www.velosklad.ru
    """

    soup = make_soup(link_for_bike)

    # Получаем название модели и бренд
    title = soup.h1.text[10:-7]
    brand = title.split()[0]

    # Получаем описание, если есть
    description = ''

    # Получаем спецификацию
    specification = {}
    spec_name = soup.find_all('div', 'ah-card-spec__name')
    spec_value = soup.find_all('div', 'ah-card-spec__value')
    for key, value in zip(spec_name, spec_value):
        if key.text.strip() in ['Скорости', 'Диаметр колес', 'Тип рамы', 'Тип вилки', 'Тип ободов', 'Тип тормозов',
                                'Ход вилки', 'Педали', 'Цвета выпускаемые', 'Размеры выпускаемые', 'Разработка',
                                'Производство', 'Максимальный вес велосипедиста']:
            continue
        specification[key.text.strip()] = ' '.join(value.contents[0].split())

    # Получаем ссылки на изображения
    images = []

    a_images = soup.find('div', 'ah-card-slider-thumbs__wrapper swiper-wrapper').find_all('a', 'prevFoto')
    for a_image in a_images:
        images.append(a_image['href'])

    return make_desc_dict(link_for_bike, brand, title, description, specification, images)


def merida_parse(link_for_bike: str) -> dict:
    """
    Функция парсит сайт https://www.merida-bikes.com
    """
    
    soup = make_soup(link_for_bike)
    
    # Получаем название модели
    title = soup.h1.text.strip().title()

    # Получаем описание, если есть
    list_p = soup.find(id='product-marketing-text').find_all('p')
    description = ''
    if list_p:
        for p in list_p:
            description += p.text
    
    # Получаем спецификацию
    specification = {}
    spec_name = soup.find_all('span', 'specification-name')
    spec_value = soup.find_all('span', 'specification-value')
    for key, value in zip(spec_name, spec_value):
        specification[key.text] = value.text

    # Получаем ссылки на изображения
    images = [soup.find('img', 'bike-variant-header-image')['src']]

    # Затем изображения других цветов
    other_images = soup.find_all('a', 'product-variant-color-item')
    for image in other_images:
        new_url = urljoin(link_for_bike, image['href'])
        new_soup = make_soup(new_url)
        images.append(new_soup.find('img', 'bike-variant-header-image')['src'])

    return make_desc_dict(link_for_bike, 'Merida', title, description, specification, images)


def giant_parse(link_for_bike: str) -> dict:
    """
    Функция парсит сайт https://www.giant-bicycles.com
    """
    
    soup = make_soup(link_for_bike, selenium=True)

    # Получаем название модели
    title = soup.h1.text

    # Получаем описание, если есть
    description = soup.h2.next_sibling.text
    
    # Получаем спецификацию
    specification = {}
    keys = soup.find_all('div', 'label')
    values = soup.find_all('div', 'value')
    for key, value in zip(keys, values):
        specification[key.text] = value.text
    
    # Получаем ссылки на изображения
    images = []
    tags_li = soup.find_all('li', 'ng-scope')
    for li in tags_li:
        images.append(li.img['src'].replace('h_60,q_90,w_60', 'h_850,q_90'))

    return make_desc_dict(link_for_bike, 'Giant', title, description, specification, images)


def techteam_parse(link_for_bike: str) -> dict:
    """
    Функция парсит сайт https://www.techteam.ru
    """

    soup = make_soup(link_for_bike)

    # Получаем название модели
    title = soup.h1.text
    title = clean_title(title, 'tt')

    # Получаем описание, если есть
    description = ''
    div_desc = soup.find('div', 'product-description__content rte')
    if div_desc:
        for p in div_desc:
            description += p.text
    description = description.strip()

    # Получаем спецификацию
    specification = {}
    sub_titles_specs = soup.find('div', 'rte chars-description').find_all('h4')
    for title_spec in sub_titles_specs:
        category = title_spec.text

        category_dict = {}
        for li in title_spec.next_sibling.find_all('li'):
            key = li.strong.text
            value = li.contents[1][3:]
            category_dict[key] = value
        specification[category] = category_dict

    # Получаем ссылки на изображения
    images = []
    a_images = soup.find_all('a', 'swiper-slide-content')
    for a in a_images:
        images.append(a.img['src'])

    return make_desc_dict(link_for_bike, 'Tech Team', title, description, specification, images)


def forward_parse(link_for_bike: str) -> dict:
    """
    Функция парсит сайт https://forwardvelo.ru
    """
    
    soup = make_soup(link_for_bike)
    
    # Получаем название модели
    title = soup.h1.text.replace(',', '.')[:-7].title()

    # Получаем описание, если есть
    description = ''

    # Получаем спецификацию
    specification = {}
    table_spec = soup.find('div', 'char-table__all')
    categories_names = table_spec.find_all('div', 'char-table__name')
    for category in categories_names:
        specification[category.span.text] ={}

    table_keys = table_spec.find_all('div', 'char-table__title')
    table_values = table_spec.find_all('div', 'char-table__text')
    for key, value in zip(table_keys, table_values):
        category_name = key.find_previous('div', 'char-table__name').span.text
        specification[category_name][key.text] = value.text
    
    # Получаем ссылки на изображения
    images = []
    images_links = soup.find_all('img', 'velo-detail-slider-main__item')
    for image in images_links:
        images.append(urljoin(link_for_bike, image['src']))
    
    return make_desc_dict(link_for_bike, 'Forward', title, description, specification, images)


def stels_parse(link_for_bike: str) -> dict:
    """
    Функция парсит сайт https://stelsbicycle.ru/
    """
    
    soup = make_soup(link_for_bike)

    # Получаем название модели
    title = soup.h2.text.replace('"', '')

    # Получаем описание, если есть
    description = ''

    # Получаем спецификацию
    specification = {}
    div_specs = soup.find_all('div', 'product-card__tr')
    for div_tr in div_specs:
        specification[div_tr.div.text] = div_tr.div.next_sibling.next_sibling.text

    # Получаем ссылки на изображения
    images = []
    links_images = soup.find_all('a', 'zoom')
    for link in links_images:
        images.append(urljoin(link_for_bike, link['href']))
    
    return make_desc_dict(link_for_bike, 'Stels', title, description, specification, images)


def stels_rf_parse(link_for_bike: str) -> dict:
    """
    Функция парсит сайт https://stels-rf.ru
    """
    
    soup = make_soup(link_for_bike)

    # Получаем название модели
    title = soup.h1.span.text.strip().replace('"', '')
    import re
    title = re.sub('\s\(.+\)$', '', title)

    # Получаем описание, если есть
    description = ''

    # Получаем спецификацию
    specification = {}
    table_spec = soup.find_all('li', 'cell')
    for li in table_spec:
        specification[li.span.span.text] = li.span.next_sibling.next_sibling.text

    # Получаем ссылки на изображения
    images = []
    images.append(soup.find('div', 'product_image').a['href'])
    
    other_images = soup.find_all('a', 'images_link')
    if other_images:
        for image in other_images:
            images.append(image['href'])


    return make_desc_dict(link_for_bike, 'Stels', title, description, specification, images)


def desna_parse(link_for_bike: str) -> dict:
    """
    Функция парсит сайт https://desnarussia.ru
    """
    
    soup = make_soup(link_for_bike)

    # Получаем название модели
    title = soup.h1.text.replace('"', '')
    if 'Десна Вояж' in title:
        title = title.replace('Десна Вояж', 'Desna Voyage')
    elif 'Десна Круиз' in title:
        title = title.replace('Десна Круиз', 'Desna Kruiz')
    elif 'Десна Спутник' in title:
        title = title.replace('Десна Спутник', 'Desna Sputnik')
    elif 'Десна Метеор' in title:
        title = title.replace('Десна Метеор', 'Desna Meteor')
    elif 'Десна Феникс' in title:
        title = title.replace('Десна Феникс', 'Desna Feniks')
    elif 'Десна' in title:
        title = title.replace('Десна', 'Desna')

    # Получаем описание, если есть
    description = ''

    # Получаем спецификацию
    specification = {}
    specs = soup.find_all('div', 'table-object')
    for spec in specs:
        specification[spec.span.text] = spec.find('div', 'col-sm-7').text

    # Получаем ссылки на изображения
    images = []
    links_images = soup.find_all('a', 'cloud-zoom')
    for link in links_images:
        images.append(urljoin(link_for_bike, link['href']))
    
    return make_desc_dict(link_for_bike, 'Desna', title, description, specification, images)


def stinger_parse(link_for_bike: str) -> dict:
    """
    Функция парсит сайт https://stingerbike.ru
    """
    
    soup = make_soup(link_for_bike, selenium=True)

    # Получаем название модели
    title = soup.title.text
    title = clean_title(title, 'stinger')

    # Получаем описание, если есть
    description = soup.find('div', 'description-text').text.strip()

    # Получаем спецификацию
    specification = {}
    tags_tr = soup.find_all('tr')
    for tr in tags_tr:
        specification[tr.td.text.strip()] = tr.td.next_sibling.next_sibling.text.strip()

    # Получаем ссылки на изображения
    images = []
    link = soup.find('a', 'fancybox')['href']
    images.append(urljoin(link_for_bike, link))

    return make_desc_dict(link_for_bike, 'Stinger', title, description, specification, images)


if __name__ == '__main__':

    def parse_and_save_files(link_for_bike: str) -> None:
        """Функция вызывает подходящую функцию парсинга и функции сохранения файлов"""
        
        if 'https://www.merida-bikes.com' in link_for_bike:
            describe_dict = merida_parse(link_for_bike)
        elif 'https://www.giant-bicycles.com' in link_for_bike:
            describe_dict = giant_parse(link_for_bike)
        elif 'https://www.techteam.ru' in link_for_bike:
            describe_dict = techteam_parse(link_for_bike)
        elif 'https://forwardvelo.ru' in link_for_bike:
            describe_dict = forward_parse(link_for_bike)
        elif 'https://stelsbicycle.ru/' in link_for_bike:
            describe_dict = stels_parse(link_for_bike)
        elif 'https://stels-rf.ru' in link_for_bike:
            describe_dict = stels_rf_parse(link_for_bike)
        elif 'https://desnarussia.ru' in link_for_bike:
            describe_dict = desna_parse(link_for_bike)
        elif 'https://stingerbike.ru' in link_for_bike:
            describe_dict = stinger_parse(link_for_bike)
        elif 'https://www.velosklad.ru' in link_for_bike:
            describe_dict = velosklad_parse(link_for_bike)
        else:
            print('[Ошибка] Не подходящая ссылка:', link_for_bike)
        
        save_json_file(describe_dict)
        if SAVE_TABLE_VIEW:
            save_table_view(describe_dict)
        download_images(describe_dict)

    import sys

    # Если запустить файл с дополнительным аргументом (название файла со ссылками на страницы),
    # программа пройдет по всем ссылкам, спарсит и сохранит данные
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        with open(sys.argv[1], 'r') as f:
            links_for_bikes = f.readlines()
        
        for link_for_bike in links_for_bikes:
            parse_and_save_files(link_for_bike.strip())
    # Если запустить файл без аргументов, программа в цикле предлагает ввести ссылку и парсит данные
    else:
        while True:
            print('Введите ссылку на страницу модели или "q" для выхода')
            link_for_bike = input('> ')

            if link_for_bike == 'q':
                break
            else:
                parse_and_save_files(link_for_bike)
