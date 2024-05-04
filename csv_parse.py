""" Парсит файл с характеристиками STELS
"""

import csv


STELS = 'specs/stels.csv'
STELS_KIDS = 'specs/stels_kids.csv'

SAVE_STELS = 'output/stels/stels_2023.txt'
SAVE_STELS_KIDS = 'output/stels/stels_kids_2023.txt'

STOP_SPECS = ['Пол', 'Амортизация', 'Категория', 'Вид велосипеда', 'Цвета для каталога',
              'Размер рамы велосипеда', 'Тип шифтеров', 'Тип тормозов', 'Розничная цена', 'Возраст']

def main(file_csv: str, save_to_file: str):
    # читаем csv-файл и заносим строку с названиями велосипедов в keys, а остальные строки в stels
    # за исключением не нужных параметров из STOP_SPECS
    with open(file_csv) as f:
        reader = csv.reader(f)
        keys = next(reader)
        stels = []
        for row in reader:
            if row[0] not in STOP_SPECS:
                stels.append(row)

    # Создаем пустую строку, в которую будем добавлять характеристики велосипедов с нужными тегами
    specs = ''

    # проходим по списку с названиями велосипедов
    for i, key in enumerate(keys):
        # пропускаем первую строку, т.к. это заголовок столбца категорий
        if i == 0:
            continue

        # записываем название велосипеда
        value = key

        for row in stels:
            # некоторые названия меняем на "нормальные"
            if row[0] == 'Переключатель скоростей передний':
                row[0] = 'Передний переключатель'
            elif row[0] == 'Переключатель скоростей задний':
                row[0] = 'Задний переключатель'
            elif row[0] == 'Вилка передняя':
                row[0] = 'Вилка'
            # дописываем характеристики с табличными тегами
            value += f'\n<tr><td>{row[0]}</td><td>{row[i]}</td></tr>'
        value += '\n\n'
        # добавляем полученную строку с характеристиками одного велосипеда к основной строке
        specs += value

    # записываем полученную строку в файл
    with open(save_to_file, 'w', encoding='utf8') as f:
        f.write(specs)

if __name__ == "__main__":
    main(STELS, SAVE_STELS)
    main(STELS_KIDS, SAVE_STELS_KIDS)