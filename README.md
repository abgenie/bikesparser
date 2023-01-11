# Bikesparser

Парсер помогает получить информацию в структурированном виде, для дальнейшего добавления на сайт. Скрипт делал для личного использования, т.ч. могут встречаться не очевидные элементы))

## Установка

```bash
git clone https://github.com/abgenie/bikesparser.git
cd bikesparser
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## Может парсить следующие сайты

- https://www.merida-bikes.com
- https://www.giant-bicycles.com
- https://www.techteam.ru
- https://forwardvelo.ru
- https://stelsbicycle.ru/
- https://stels-rf.ru
- https://desnarussia.ru
- https://stingerbike.ru

## Получает данные

- Название велосипеда
- Описание (если есть на сайте)
- Спецификацию велосипеда
- Скачивает изорбажения

## Результат работы

- Файл json со следующим содержанием:
  - url: str
  - brand: str
  - model_year: str
  - title: str
  - description: str
  - specification: dict
  - images: list
- Изображения велосипеда

## Варианты работы

1. Если при запуске скрипта в параметре передать название файла, то скрипт спарсит все ссылки из файла. Файл должен содержать ссылки на страницу велосипеда, каждая с новой строки.
2. Если запустить скрипт без параметров, то скрипт в цикле будет предлагать ввести ссылку на велосипед и сразу парсить данные и т.д.

## Настройки

В файле 'helpers.py' есть константы, которые можно изменять:
- **BRAND_DIR: bool** если *True*, то файлы будут сохраняться в подкаталоги с название бренда велосипеда, иначе в одну папку *output*.
- **MODEL_YEAR: str** для добавления года к названиям файлов. Год указываю вручную, т.к. в описаниях моделей часто не указывается год.

## Дополнительно

На сайтах **Tech Team** и **Stinger** к названию велосипеда добавлены лишние слова *(велосипед, подростковый велосипед, самокат и т.д.)*, которые мне не нужны в названиях файлов. Чтобы получить все возможные названия, можно использовать файл **'get_titles.py'**  в интерактивном режиме. Это скрипт создает файл со списком названий, каждое с новой строки. Из него нужно вручную убрать всё лишнее, оставив только лишние слова и переместить в папку **'settings'**. Конечный результат используется при парсинге.