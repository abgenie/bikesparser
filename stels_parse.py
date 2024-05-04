from helpers import *


def stels_parse(link_for_bike: str) -> dict:
    """
    Функция парсит файл 'HTML' с сайта https://stelsbicycle.ru/
    """
    
    soup = make_soup_from_file(link_for_bike)

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
        images.append(link['href'])
    
    return make_desc_dict(link_for_bike, 'Stels', title, description, specification, images)


if __name__ == '__main__':

    # получаем список файлов в директории 
    links = os.listdir('html')

    # парсим каждый файл
    for link_for_bike in links:
        describe_dict = stels_parse(link_for_bike)

        save_json_file(describe_dict)
        if SAVE_TABLE_VIEW:
            save_table_view(describe_dict)
        download_images(describe_dict)
