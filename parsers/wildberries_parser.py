import re
import time

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def findRequiredItemFromWb(item_title):
    driver = uc.Chrome(headless=False, use_subprocess=False)
    driver.get('https://www.wildberries.ru/catalog/0/search.aspx?search=' + item_title)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article[data-nm-id]"))
        )
    except Exception:
        driver.quit()
        return
    page_html = driver.page_source
    soup = BeautifulSoup(page_html, "html.parser")
    mainCatalog = soup.find(class_="catalog-page__main")
    count_elements = mainCatalog.find_all(class_="product-card__count")
    count_values = []
    for element in count_elements:
        try:
            text = element.text.replace("\xa0", " ")  # Убираем неразрывные пробелы
            number = int("".join(filter(str.isdigit, text)))  # Извлекаем число
            count_values.append(number)
        except ValueError:
            continue  # Пропускаем элементы, которые не содержат числа

    if count_values:
        max_value = max(count_values)  # Находим максимальное значение
        max_index = count_values.index(max_value)  # Получаем его индекс
        product_elements = soup.find_all("article", attrs={"data-nm-id": True})

        # Проверяем, есть ли элемент по этому индексу
        if 0 <= max_index < len(product_elements):
            href = product_elements[max_index].find(class_='product-card__link').get("href")
            reviews = parseReviewsFromWb(href, driver)
        else:
            print("Не найден соответствующий товар по индексу.")

    else:
        print("Не найдено значений в 'product-card__count'")
    return reviews

def parseReviewsFromWb(url, driver):
    driver.get(url.split("detail.aspx")[0] + "feedbacks")
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "comments__item"))
        )
    except Exception:
        driver.quit()
        return
    page_html = driver.page_source
    driver.quit()
    soup = BeautifulSoup(page_html, "html.parser")
    reviews = soup.find_all(class_="j-feedback__text")
    for i in range(len(reviews)):
        reviews[i] = reviews[i].text
    return reviews
