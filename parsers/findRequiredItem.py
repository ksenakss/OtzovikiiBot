import re
import time
import concurrent.futures
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from parsers.ozon_parser import findRequiredItemFromOzon
from parsers.wildberries_parser import findRequiredItemFromWb

def findRequiredItem(item):
    item = item.replace(" ", "%")
    driver = uc.Chrome(headless=False, use_subprocess=False)
    driver.get('https://www.wildberries.ru/catalog/0/search.aspx?search=' + item)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article[data-nm-id]"))
        )
    except Exception:
        driver.quit()
        return
    page_html = driver.page_source
    driver.quit()
    soup = BeautifulSoup(page_html, "html.parser")

    product_elements = soup.find("article", attrs={"data-nm-id": True})
    href = product_elements.find(class_='product-card__link').get("href")
    photo = product_elements.find(class_='j-thumbnail').get("src")
    return href, photo

    # Извлекаем числовые значения и находим максимальное
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
            photo = product_elements[max_index].find(class_='j-thumbnail').get("src")
            return href, photo
        else:
            print("Не найден соответствующий товар по индексу.")

    else:
        print("Не найдено значений в 'product-card__count'")


def findReviewsOnMarketplaces(url):
    reviews = []

    driver = uc.Chrome(headless=False, use_subprocess=False)
    driver.get(url)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "product-page__title"))
        )
    except Exception:
        driver.quit()
        return
    page_html = driver.page_source
    soup = BeautifulSoup(page_html, "html.parser")
    item_title = soup.find(class_="product-page__title").text

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_wb = executor.submit(findRequiredItemFromWb, item_title)
        future_ozon = executor.submit(findRequiredItemFromOzon, item_title)

        print(future_wb.result(), future_ozon.result())
        reviews += future_wb.result()
        reviews += future_ozon.result()

    # #wb part
    # reviews = reviews + findRequiredItemFromWb(item_title=item_title)
    #
    # #ozon part
    # findRequiredItemFromOzon(item_title=item_title)

    driver.quit()
    return reviews

# if __name__ == "__main__":
#     findRequiredItemOnMarketplaces("https://www.wildberries.ru/catalog/34939243/detail.aspx")