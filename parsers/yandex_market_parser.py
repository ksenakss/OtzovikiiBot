from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from parsers.findRequiredItem import init_driver

def findRequiredItemFromYandex(item_title):
    driver = init_driver()
    driver.get(f"https://market.yandex.ru/search?text={item_title}")

    # Прокрутка вниз страницы
    for _ in range(3):  # Прокручиваем 3 раза
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
        time.sleep(1)  # Ждем, чтобы контент успел загрузиться

    # Поиск товаров
    products = driver.find_elements(By.CSS_SELECTOR, 'div.n-snippet-card2')
    reviews_count = []

    for product in products[:5]:  # Берем только первые 5 товаров
        title = product.find_element(By.CSS_SELECTOR, 'h3.n-snippet-card2__title').text
        try:
            reviews = product.find_element(By.CSS_SELECTOR, 'span.n-snippet-card2__rating').text
            reviews_count.append((title, int(reviews.split()[0])))  # Сохраняем название и количество отзывов
        except:
            reviews_count.append((title, 0))  # Если отзывов нет, ставим 0

    # Находим товар с наибольшим количеством отзывов
    if reviews_count:
        most_reviewed_product = max(reviews_count, key=lambda x: x[1])
        return most_reviewed_product[0], most_reviewed_product[1]
    return None, 0
