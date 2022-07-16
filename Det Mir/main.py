import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from re import *
import csv


# Я реализовал данный парсер не универсальным и быстрым, так как пришлось использовать selenium webdriver.
# Сделал я это, потому что сайт https://www.detmir.ru/ не хотел выдавать данные по другому

# Ссылка для установки Google Chrome 104.0.5112.48 https://www.google.ru/intl/ru/chrome/beta/

URL = 'https://www.detmir.ru/catalog/index/name/lego/'
url1 = "https://api.detmir.ru/v2/recommendation/products?filter=category.id:40;placement:web_listing_popular;region.iso:RU-MOW&limit=30"


def get_source_html(url):
    # Функция для получения изначального HTML кода нужной страницы сайта

    service = Service("Components/chromedriver_win32/chromedriver.exe")
    # Этот путь находится в проекте, поэтому он будет работать на любом компьютере

    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.binary_location = "C:\Program Files\Google\Chrome Beta\Application\chrome.exe"
    # А этот путь будет работать на любом Windows компьютере, на котором установлен Chrome Browser (версия 104.0.5112.48)

    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url=url)
        time.sleep(5)

        for i in range(17):
            btn_show_more = driver.find_element(By.CLASS_NAME, 'g_1.g_5.hk.hb.ht.hv.he')
            action = ActionChains(driver)
            action.move_to_element(btn_show_more)
            btn_show_more.click()
            time.sleep(3)

        with open("Components/Pages/source-page.html", "w") as file:
            file.write(driver.page_source)    

        return ">>>Source html received successfully!<<<"

    except Exception as e:
        print(e)
    finally:
        driver.close()
        driver.quit()


def get_items_urls(file_path):
    # Функция для получения ссылок товаром со страницы

    with open(file_path, encoding="utf-8") as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')

    items_divs_containers = soup.find_all('div', class_='vW')

    urls = []
    for item in items_divs_containers:
        item_url = item.find('div', class_='vY').find('a').get('href')
        urls.append(item_url)

    # with open("Components/Result files/urls.txt", "w") as file:
    #     for url in urls:
    #         file.write(f"{url}\n")

    return urls


def get_items_id(file_path):
    # Функция для получения id товаров. Я взял id из ссылок на товары, не нашел другого места где упоминались id товаров

    with open(file_path) as file:
        url_list = [url.strip() for url in file.readlines()]

    ids = []
    for i in url_list:
        id = i.split('d')[-1].strip('/')
        ids.append(id)

    # with open("Components/Result files/ids.txt", 'w') as file:
    #     for id in ids:
    #         file.write(f'{id}\n')

    return ids


def get_items_names(file_path):
    # Функция  для получения наименования каждого товара со страницы

    with open(file_path, encoding="utf-8") as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')

    items_divs = soup.find_all('div', class_='Ru')

    names = []
    for item in items_divs:
        name = item.findNext('div', 'RQ').find('p').text
        names.append(name)

    # with open("Components/Result files/names.txt", 'w', encoding="utf-8") as file:
    #     for name in names:
    #         file.write(f"{name}\n")

    return names


def get_items_prices_default(file_path):
    # Функция для получения цен товаров без скидки

    with open(file_path, encoding="utf-8") as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')

    items_divs_prices_default = soup.find_all('div', class_='RQ')
    items_divs_prices_default.reverse()
    items_divs_prices_default = items_divs_prices_default[::2]
    items_divs_prices_default.reverse()

    prices_default = []
    for item in items_divs_prices_default:
        divs_of_prices = item.find('div', class_='RE')
        if divs_of_prices is not None:
            prices_promo_and_default = divs_of_prices.find('div', class_='Rz').find_all('p')
            prices_promo_and_default.reverse()
            prices_promo_and_default = prices_promo_and_default[::2]
            for price in prices_promo_and_default:
                price_default = price.text
            price_default = "".join(i for i in price_default if i.isdecimal())
        else:
            price_default = 'Товара нет в наличии'
        prices_default.append(price_default)

    with open("Components/Result files/prices_default.txt", 'w', encoding="utf-8") as file:
        for price in prices_default:
            file.write(f"{price}\n")

    return prices_default


def get_items_prices_promo(file_path):
    # Функция для получения цен товаров со скидкой

    with open(file_path, encoding="utf-8") as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')

    items_divs_prices_promo = soup.find_all('div', class_='RQ')
    items_divs_prices_promo.reverse()
    items_divs_prices_promo = items_divs_prices_promo[::2]
    items_divs_prices_promo.reverse()

    prices_promo = []
    for item in items_divs_prices_promo:
        divs_of_prices = item.find('div', class_='RE')
        if divs_of_prices is not None:
            if divs_of_prices.find('div', class_='Rz').find('p', class_="RB"):
                price_promo = divs_of_prices.find('div', class_='Rz').find('p').text
                price_promo = "".join(i for i in price_promo if i.isdecimal())
            else:
                price_promo = ''
        else:
            price_promo = ''
        prices_promo.append(price_promo)

    # with open("Components/Result files/prices_promo.txt", 'w', encoding="utf-8") as file:
    #     for price in prices_promo:
    #         file.write(f"{price}\n")

    return prices_promo


def create_csv_results(ids, names, prices, prices_promo, urls):
    # Функция создающая csv файл со всеми результатами

    zip_lists = zip(ids, names, prices, prices_promo, urls)
    csv_file = csv.writer(open('Components/Result files/results.csv', 'w'), lineterminator="\r", delimiter=",")
    csv_file.writerow(['id, title, price, promo_price, url'])
    for list in zip_lists:
        csv_file.writerow(list)

    return "All complete!"

def main():
    print(get_source_html(url=URL))
    urls = get_items_urls(file_path="Components/Pages/source-page.html")
    ids = get_items_id(file_path="Components/Result files/urls.txt")
    names = get_items_names(file_path="Components/Pages/source-page.html")
    prices = get_items_prices_default(file_path="Components/Pages/source-page.html")
    prices_promo = get_items_prices_promo(file_path="Components/Pages/source-page.html")
    print(create_csv_results(ids, names, prices, prices_promo, urls))


if __name__ == "__main__":
    main()
