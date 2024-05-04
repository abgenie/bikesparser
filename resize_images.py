""" Меняет разрешение изображений на указанное в IMAGE_SIZE.
    В параметре нужно передать папку с изображениями или одно изображение
"""

import sys, os
from PIL import Image


IMAGE_SIZE = (1240, 697)
EXTS = ('.jpg', '.jpeg', '.png', '.PNG', '.JPG', '.JPEG')


def resize(file: str) -> None:
    image = Image.open(file)
    
    # если изображение нужного размера, то выходим
    if image.size == IMAGE_SIZE:
        print(f'Изображение уже нужного размера: "{file}"')
        return

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

    # Создаём белый фон нужного размера, ресайзим изображение и помещаем по центру фона
    new_image = Image.new('RGB', IMAGE_SIZE, (255, 255, 255))
    offset = ((IMAGE_SIZE[0] - size[0]) // 2, (IMAGE_SIZE[1] - size[1]) // 2)
    new_image.paste(image.resize(size), offset)

    # сохраняем c тем же именем и расширением 'jpg'
    new_image.save(file, 'JPEG')
    print(f'Save image: {file}')


if __name__ == "__main__":
    # проверяем передан ли параметр
    if len(sys.argv) > 1:
        target = sys.argv[1]
        
        # если передана папка, то ресайзим все файлы с расширениями из EXTS
        if os.path.isdir(target):
            # добавляем слеш в конце, если не указан
            if target[-1:] != '/':
                target = target + '/'
            
            files = os.listdir(target)
            for file in files:
                if os.path.splitext(file)[1] in EXTS:
                    resize(f'{target}{file}')
        # если передан файл, то ресайзим его
        else:
            if os.path.splitext(target)[1] in EXTS:
                resize(target)
            else:
                print('Указан не подходящий файл:')
                print(target)
                print(f'Поддерживаемые разрешения: {EXTS}')

    # если не передан параметр, то выходим
    else:
        print('Не указана папка или файл в аргументе при запуске скрипта!')
        sys.exit(1)