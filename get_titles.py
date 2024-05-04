from selenium.webdriver.common.by import By
from helpers import *


def save_list_in_file(names: list, filename: str) -> None:
    """
    Функция сохраняет список в файл построчно
    """
    with open('settings/' + filename, 'a') as f:
        for name in names:
            f.write(name + '\n')


# Stinger

def get_stinger_titles() -> None:
    """
    Функция получает названия всех велосипедов с сайта https://stingerbike.ru/ и сохраняет в файл
    """
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    
    driver.get('https://stingerbike.ru/catalog/velosipedy/')
    names = []

    while True:
        divs_names = driver.find_elements(By.CLASS_NAME, 'name')
        
        for name in divs_names:
            names.append(name.text)
            print(name.text)
        try:
            driver.find_element(By.XPATH, "//li[@class='active']/following-sibling::li").click()
        except:
            break
        
    driver.quit()
    names.sort()

    save_list_in_file(names, 'bikes_names_stinger_new.txt')


# Tech Team

def get_pages_in_category(url: str) -> list:
    """
    Функция проходит по всем страницам категории сайта https://www.techteam.ru и возвращает 
    список ссылок на страницы товаров
    """
    soup = make_soup(url)
    pages = []
    for page_url in soup.find_all('a', 'productPlate_name'):
        pages.append('https://www.techteam.ru/' + page_url['href'])
        
    try:
        next_button = soup.find('ul', 'pagination').find('li', 'active').next_sibling
        if not 'disabled' in next_button['class']:
            pages.extend(get_pages_in_category(next_button.a['href']))
    except AttributeError:
        pass

    return pages


def get_all_pages() -> None:
    """
    Функция получает ссылки на все велосипеды и самокаты с сайта https://www.techteam.ru
    и сохраняет в файл
    """
    soup = make_soup('https://www.techteam.ru')
    links_scooters_categories = soup.find('li', 'parent parent-13').ul.find_all('a')
    links_bikes_categories = soup.find('li', 'parent parent-26').ul.find_all('a')

    # Получаем ссылки на страницы категорий
    all_categories_urls = []
    for link_scooter_category in links_scooters_categories:
        if 'zapchasti' in link_scooter_category['href']:
            continue
        all_categories_urls.append(link_scooter_category['href'])
    for link_bike_category in links_bikes_categories:
        if 'aksessuaryi' in link_bike_category['href'] or 'zapchasti' in link_bike_category['href']:
            continue
        all_categories_urls.append(link_bike_category['href'])
    
    all_categories_urls.append(soup.find('a', string='Беговелы')['href'])

    # Получаем ссылки на страницы товаров
    all_pages = []
    for category in all_categories_urls:
        pages_in_category = get_pages_in_category(category)
        all_pages.extend(pages_in_category)
    
    save_list_in_file(all_pages, 'tt_all_pages.txt')


def get_tt_titles_from_file() -> None:
    """
    Функция читает файл со ссылками на страницы, и с каждой страницы сохраняет название велосипеда
    """
    with open('settings/tt_all_pages.txt', 'r') as f:
        all_pages = f.readlines()

    names = []
    try:
        for i, page in enumerate(all_pages):
            print(i, page.rstrip())
            soup = make_soup(page.rstrip())
            names.append(soup.h1.text)
    except ConnectionError as e:
        print(e)
        print('Сохранено записей', len(names))
    finally:
        names.sort()
        save_list_in_file(names, 'bikes_names_tt_new.txt')


if __name__ == '__main__':
    
    # Получаем файл со списком названий велосипедов Stinger
    get_stinger_titles()

    # Получаем файл со списком название велосипедов TT
    get_all_pages()
    get_tt_titles_from_file()
    

