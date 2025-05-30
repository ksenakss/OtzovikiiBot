from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from parsers.driver_manager import init_wb_reviews_driver

def findRequiredItemFromWb(item_title):
    driver = None
    reviews = []
    try:
        driver = init_wb_reviews_driver()
        print(f"Starting Wildberries search for: {item_title}")
        driver.get('https://www.wildberries.ru/catalog/0/search.aspx?search=' + item_title)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article[data-nm-id]"))
            )
        except Exception as e:
            print(f"Timeout waiting for product cards: {str(e)}")
            return reviews

        page_html = driver.page_source
        soup = BeautifulSoup(page_html, "html.parser")
        mainCatalog = soup.find(class_="catalog-page__main")
        
        if not mainCatalog:
            print("Не найден основной каталог")
            return reviews
            
        count_elements = mainCatalog.find_all(class_="product-card__count")
        count_values = []
        for element in count_elements:
            try:
                text = element.text.replace("\xa0", " ")
                number = int("".join(filter(str.isdigit, text)))
                count_values.append(number)
            except ValueError:
                continue

        if count_values:
            max_value = max(count_values)
            max_index = count_values.index(max_value)
            product_elements = soup.find_all("article", attrs={"data-nm-id": True})
            if 0 <= max_index < len(product_elements):
                product_link = product_elements[max_index].find(class_='product-card__link')
                if product_link and product_link.get("href"):
                    href = product_link.get("href")
                    reviews = parseReviewsFromWb(href)
                else:
                    print("Не найден URL товара")
            else:
                print("Не найден соответствующий товар по индексу.")
        else:
            print("Не найдено значений в 'product-card__count'")
    except Exception as e:
        print(f"Ошибка при поиске товара на Wildberries: {str(e)}")
    return reviews

def parseReviewsFromWb(url):
    reviews = []
    try:
        driver = init_wb_reviews_driver()
        print(f"Parsing Wildberries reviews from: {url}")
        driver.get(url.split("detail.aspx")[0] + "feedbacks")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "comments__item"))
            )
        except Exception as e:
            print(f"Timeout waiting for reviews: {str(e)}")
            return reviews

        page_html = driver.page_source
        soup = BeautifulSoup(page_html, "html.parser")
        reviews = soup.find_all(class_="j-feedback__text")
        reviews = [review.text.strip() for review in reviews if review.text.strip()]
        print(f"Found {len(reviews)} reviews on Wildberries")
    except Exception as e:
        print(f"Ошибка при парсинге отзывов: {str(e)}")
    return reviews
