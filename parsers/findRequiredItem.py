from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from parsers.ozon_parser import findRequiredItemFromOzon
from parsers.wildberries_parser import findRequiredItemFromWb
from parsers.yandex_market_parser import findRequiredItemFromYandex
from parsers.driver_manager import init_search_driver
import asyncio

def findRequiredItem(item):
    try:
        print("findRequiredItem")
        item = item.replace(" ", "%")
        driver = init_search_driver()
        print(f"Searching for item: {item}")  # Добавляем логирование
        driver.get('https://www.wildberries.ru/catalog/0/search.aspx?search=' + item)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article[data-nm-id]"))
            )
        except Exception as e:
            print(f"Timeout waiting for product elements: {str(e)}")
            return None, None

        page_html = driver.page_source
        soup = BeautifulSoup(page_html, "html.parser")

        no_results = soup.find(string=lambda text: text and "Ничего не нашлось по запросу" in text)
        if no_results:
            print("No items found for the search query")
            return "no_results", None

        product_elements = soup.find("article", attrs={"data-nm-id": True})
        if not product_elements:
            print("No product elements found on the page")
            return None, None

        href = product_elements.find(class_='product-card__link')
        photo = product_elements.find(class_='j-thumbnail')
        
        if not href or not photo:
            print("Product link or photo not found")
            return None, None

        product_url = href.get("href")
        photo_url = photo.get("src")
        print(f"Found product: {product_url}")  # Добавляем логирование
        return product_url, photo_url
    except Exception as e:
        print(f"Error in findRequiredItem: {str(e)}")
        return None, None

async def findReviewsOnMarketplaces(url, user_query=None):
    try:
        print(f"Searching reviews for URL: {url}")
        # Получаем название товара из URL
        driver = init_search_driver()
        driver.get(url)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "product-page__title"))
            )
        except Exception as e:
            print(f"Timeout waiting for product title: {str(e)}")
            return []

        page_html = driver.page_source
        soup = BeautifulSoup(page_html, "html.parser")
        item_title = soup.find(class_="product-page__title")
        
        if not item_title:
            print("Product title not found on the page")
            return []
            
        item_title = item_title.text.strip()
        print(f"Found product title: {item_title}")

        print("Fetching reviews from marketplaces...")
        
        
        wb_reviews, ozon_reviews, yandex_reviews = await asyncio.gather(
            asyncio.to_thread(findRequiredItemFromWb, item_title),
            asyncio.to_thread(findRequiredItemFromOzon, item_title),
            asyncio.to_thread(findRequiredItemFromYandex, item_title),
        )
        
        print(f"Found {len(wb_reviews) if wb_reviews else 0} WB reviews and {len(ozon_reviews) if ozon_reviews else 0} Ozon reviews and {len(yandex_reviews) if yandex_reviews else 0} Yandex reviews")

        
        reviews = []
        if wb_reviews:
            reviews.extend(wb_reviews)
        if ozon_reviews:
            reviews.extend(ozon_reviews)
        if yandex_reviews:
            reviews.extend(yandex_reviews)


        if not reviews:
            print("No reviews found from any marketplace")
        else:
            print(f"Total reviews found: {len(reviews)}")

        return reviews
    except Exception as e:
        print(f"Error in findReviewsOnMarketplaces: {str(e)}")
        return []

def cleanup():
    global driver
    if driver:
        driver.quit()
        driver = None