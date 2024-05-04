import requests, json, os, io
import urllib3
from typing import Literal
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from PIL import Image

from settings.settings import *


BRAND = Literal['stinger', 'tt']

urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)


def _get_page_with_selenium(link_for_bike: str) -> str:
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    # driver.implicitly_wait(10)
    driver.get(link_for_bike)

    page_html = driver.page_source
    driver.close()
    
    return page_html


def make_soup(link_for_bike: str, selenium=False) -> BeautifulSoup:
    """Получает ссылку на страницу и создаёт объект BeautifulSoup"""
    if selenium:
        req = _get_page_with_selenium(link_for_bike)
    else:
        req = requests.get(link_for_bike, headers={'User-Agent': 'Mozilla/5.0'}, verify=False).text
    return BeautifulSoup(req, 'lxml')


def make_soup_cube(link_for_bike: str) -> BeautifulSoup:
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(link_for_bike)

    # driver.find_element_by_class_name('#taba867c7ec857341c198a415fd921efb25_2')
    btn_component = driver.find_element_by_link_text(' COMPONENTS')
    btn_component.click()

    page_html = driver.page_source
    driver.close()

    return BeautifulSoup(page_html, 'lxml')


def make_soup_from_file(filename: str) -> BeautifulSoup:
    with open(f'html/{filename}', 'r', encoding='utf8') as f:
        req = f.read()
    return BeautifulSoup(req, 'lxml')


def clean_title(title: str, brand: BRAND) -> str:
    """Убирает лишние слова из названия велосипеда"""

    with open(f'settings/bikes_names_{brand}.txt', 'r', encoding='utf8') as f:
        for word in f:
            title = title.replace(word.rstrip() + ' ', '')

    return title


def make_desc_dict(link_for_bike: str, brand: str, title: str, description: str, specification: dict, images: list, model_year=None) -> dict:
    """Получает параметры, создает и возвращает словарь"""

    return {
        'link_for_bike': link_for_bike,
        'brand': brand,
        'model_year': model_year if model_year else MODEL_YEAR,
        'title': title,
        'description': description,
        'specification': specification,
        'images': images
    }


# Функции для сохранения данных

def resize_and_save_image(image_url: str, filename: str) -> None:
    """
    Функция меняет разрешение изображения и сохраняет его
    """

    r = requests.get(image_url, stream=True, verify=False)
    image = Image.open(io.BytesIO(r.content))

    # Если формат PNG, то убираем прозрачность и помещаем на белый фон
    if image.format == 'PNG':
        new_image = Image.new('RGBA', image.size, (255, 255, 255, 255))
        image = Image.alpha_composite(new_image, image.convert('RGBA'))

    # Находим коэффициент ресайза, и подбираем новый размер без изменения пропорций
    ratio_w = IMAGE_SIZE[0] / image.width
    ratio_h = IMAGE_SIZE[1] / image.height
    if ratio_w < ratio_h:
        size = (int(image.width * ratio_w), int(image.height * ratio_w))
    else:
        size = (int(image.width * ratio_h), int(image.height * ratio_h))

    # Создаём белый фон нужного размера и по центру помещаем скачанное изображение
    new_image = Image.new('RGB', IMAGE_SIZE, (255, 255, 255))
    offset = ((IMAGE_SIZE[0] - size[0]) // 2, (IMAGE_SIZE[1] - size[1]) // 2)
    new_image.paste(image.resize(size), offset)

    new_image.save(filename, 'JPEG')


def download_images(describe_dict: dict) -> None:
    """
    Функция получает словарь и скачивает изображения
    """
    title = describe_dict['title'].replace(' ', '_').lower()
    brand = describe_dict['brand'].replace(' ', '_').lower()

    if BRAND_DIR:
        if not os.path.exists(f'output/{brand}'):
            os.makedirs(f'output/{brand}')
        filename_prefix = f'output/{brand}/{title}_{MODEL_YEAR}_'
    else:
        filename_prefix = f'output/{brand}_{title}_{MODEL_YEAR}_'
    
    for i, image_url in enumerate(describe_dict['images'], 1):
        extention = image_url.split('.')[-1]
        if extention == 'png' and not RESIZE_IMAGES:
            filename = filename_prefix + str(i) + '.png'
        else:
            filename = filename_prefix + str(i) + '.jpg'
        
        if RESIZE_IMAGES:
            resize_and_save_image(image_url, filename)
            print('Загружено изображение:', IMAGE_SIZE, filename)
        else:
            with open(filename, 'wb', encoding='utf8') as f:
                f.write(requests.get(image_url, verify=False).content)
            print('Загружено изображение:', filename)


def save_json_file(describe_dict: dict) -> None:
    """
    Функция получает словарь и сохраняет его в JSON-файл
    """
    title = describe_dict['title'].replace(' ', '_').lower()
    brand = describe_dict['brand'].replace(' ', '_').lower()
    
    if BRAND_DIR:
        if not os.path.exists(f'output/{brand}'):
            os.makedirs(f'output/{brand}')
        filename = f'output/{brand}/{title}_{MODEL_YEAR}.json'
    else:
        filename = f'output/{brand}_{title}_{MODEL_YEAR}.json'

    with open(filename, 'w', encoding='utf8') as f:
        json.dump(describe_dict, f, ensure_ascii=False, indent=4)
        print('\nСоздан файл:', filename)


def save_table_view(describe_dict: dict) -> None:
    """
    Функция сохраняет файл TXT с описанием и спецификациями, оформленными в теги <tr> и <td>
    """
    result = ''
    if describe_dict['description']:
        result += describe_dict['description'] + '\n\n'
    
    for key, value in describe_dict['specification'].items():
        if isinstance(value, dict):
            result += f'<tr><th colspan="2">{key}</th></tr>\n'
            for sub_key, sub_value in value.items():
                result += f'<tr><td>{sub_key}</td><td>{sub_value}</td></tr>\n'
        else:
            result += f'<tr><td>{key}</td><td>{value}</td></tr>\n'
    
    title = describe_dict['title'].replace(' ', '_').lower()
    brand = describe_dict['brand'].replace(' ', '_').lower()
    
    if BRAND_DIR:
        if not os.path.exists(f'output/{brand}'):
            os.makedirs(f'output/{brand}')
        filename = f'output/{brand}/{title}_{MODEL_YEAR}.txt'
    else:
        filename = f'output/{brand}_{title}_{MODEL_YEAR}.txt'

    with open(filename, 'w', encoding='utf8') as f:
        f.write(result)
        print('Создан файл:', filename)
