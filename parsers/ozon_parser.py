import re
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from parsers.driver_manager import init_ozon_reviews_driver

def findRequiredItemFromOzon(item_title):
    driver = None
    reviews = []
    try:
        driver = init_ozon_reviews_driver()
        print(f"Starting Ozon search for: {item_title}")
        driver.get("https://www.ozon.ru/search/?text=" + item_title + "&from_global=true")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "contentScrollPaginator"))
            )
        except Exception as e:
            print(f"Timeout waiting for Ozon search results: {str(e)}")
            return reviews

        page_html = driver.page_source
        soup = BeautifulSoup(page_html, "html.parser")
        review_elements = soup.find_all(string=re.compile(r'\d+\s*(?:отзывов|отзыва)'))
        count_reviews = []
        for element in review_elements:
            try:
                text = element.text.replace("\xa0", " ")
                number = int("".join(filter(str.isdigit, text)))
                count_reviews.append(number)
            except ValueError:
                continue
        if count_reviews:
            max_value = max(count_reviews)
            print(f"Found product with {max_value} reviews")
            max_index = count_reviews.index(max_value)
            product_elements = soup.find_all(class_="tile-root")
            if 0 <= max_index < len(product_elements):
                product_link = product_elements[max_index].find("a")
                if product_link and product_link.get("href"):
                    href = product_link.get("href").split("?")[0]
                    reviews = parseReviewsFromOzon("https://www.ozon.ru" + href + "reviews/")
                else:
                    print("Не найден URL товара")
            else:
                print("Не найден соответствующий товар по индексу.")
        else:
            print("Не найдено значений отзывов")
    except Exception as e:
        print(f"Ошибка при поиске товара на Ozon: {str(e)}")
    return reviews

def parseReviewsFromOzon(url):
    reviews = []
    try:
        driver = init_ozon_reviews_driver()
        print(f"Parsing Ozon reviews from: {url}")
        driver.get(url)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-review-uuid]"))
            )
        except Exception as e:
            print(f"Timeout waiting for Ozon reviews: {str(e)}")
            return reviews

        page_html = driver.page_source
        soup = BeautifulSoup(page_html, "html.parser")
        reviews = soup.find_all("div", attrs={"data-review-uuid": True})
        reviews = [review.text.strip() for review in reviews if review.text.strip()]
        print(f"Found {len(reviews)} reviews on Ozon")
    except Exception as e:
        print(f"Ошибка при парсинге отзывов Ozon: {str(e)}")
    return reviews
