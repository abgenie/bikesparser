import requests, json, os
import urllib3
from typing import Literal
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager


BRAND_DIR = True  # Если True, то сохраняет файлы в папку с название бренда
MODEL_YEAR = '2022'  # Для добавления к названиям файлов

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
    
    for i, image in enumerate(describe_dict['images'], 1):
        filename = filename_prefix + str(i) + '.jpg'
        with open(filename, 'wb') as f:
            f.write(requests.get(image, verify=False).content)
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

    with open(filename, 'w') as f:
        json.dump(describe_dict, f, ensure_ascii=False, indent=4)
        print('Создан файл:', filename)
