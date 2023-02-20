import requests, json, os
import urllib3
from typing import Literal
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager

from PIL import Image

from settings.settings import *


BRAND = Literal['stinger', 'tt']

urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

# Вспомогательные функции

def _get_page_with_selenium(url: str) -> str:

    # Для установки драйвера раскоментировать и 
    # добавить параметр'service=service' в webdriver.Firefox()    
    # service=FirefoxService(GeckoDriverManager().install())
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.implicitly_wait(10)
    driver.get(url)

    page_html = driver.page_source

    driver.quit()
    
    return page_html


def make_soup(url: str, selenium=False) -> BeautifulSoup:
    """
    Функция принимает ссылку на страницу и создаёт объект BeautifulSoup
    """
    if selenium:
        req = _get_page_with_selenium(url)
    else:
        req = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, verify=False).text
    return BeautifulSoup(req, 'lxml')


def clean_title(title: str, brand: BRAND) -> str:
    """
    Функция убирает лишние слова из названия велосипеда
    """
    with open(f'settings/bikes_names_{brand}.txt', 'r') as f:
        words = f.readlines()

    for word in words:
        title = title.replace(word.rstrip() + ' ', '')

    return title


def make_desc_dict(url: str, brand: str, title: str, description: str, specification: dict, images: list) -> dict:
    """
    Функция принимает параметры, создает и возвращает словарь
    """
    return {
        'url': url,
        'brand': brand,
        'model_year': MODEL_YEAR,
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

    image = Image.open(requests.get(image_url, stream=True, verify=False).raw)

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
            with open(filename, 'wb') as f:
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
