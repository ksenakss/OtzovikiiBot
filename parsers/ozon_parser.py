import re
import time

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def findRequiredItemFromOzon(item_title):
    driver = uc.Chrome(headless=False, use_subprocess=False)
    driver.get("https://www.ozon.ru/search/?text=" + item_title + "&from_global=true")
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "contentScrollPaginator"))
        )
    except Exception:
        driver.quit()
        return
    page_html = driver.page_source
    soup = BeautifulSoup(page_html, "html.parser")
    review_elements = soup.find_all(string=re.compile(r'\d+\s*отзывов'))
    count_reviews = []
    for element in review_elements:
        try:
            text = element.text.replace("\xa0", " ")  # Убираем неразрывные пробелы
            number = int("".join(filter(str.isdigit, text)))  # Извлекаем число
            count_reviews.append(number)
        except ValueError:
            continue  # Пропускаем элементы, которые не содержат числа
    if count_reviews:
        max_value = max(count_reviews)  # Находим максимальное значение
        print(max_value)
        max_index = count_reviews.index(max_value)  # Получаем его индекс
        product_elements = soup.find_all(class_="tile-root")
        # Проверяем, есть ли элемент по этому индексу
        if 0 <= max_index < len(product_elements):
            href = product_elements[max_index].find("a").get("href").split("?")[0]
            reviews = parseReviewsFromOzon("https://www.ozon.ru" + href + "reviews/", driver)
        else:
            print("Не найден соответствующий товар по индексу.")

    else:
        print("Не найдено значений в 'product-card__count'")
    return reviews

def parseReviewsFromOzon(url, driver):
    driver.get(url)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-review-uuid]"))
        )
    except Exception:
        driver.quit()
        return
    page_html = driver.page_source
    driver.quit()
    soup = BeautifulSoup(page_html, "html.parser")
    reviews = soup.find_all("div", attrs={"data-review-uuid": True})
    for i in range(len(reviews)):
        reviews[i] = reviews[i].text
    return reviews
