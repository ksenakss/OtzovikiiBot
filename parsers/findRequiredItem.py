import re
import time
import concurrent.futures
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from parsers.ozon_parser import findRequiredItemFromOzon
from parsers.wildberries_parser import findRequiredItemFromWb
from db_handler.main_handler import get_cached_reviews, cache_reviews
from parsers.driver_manager import init_driver
import asyncio

def findRequiredItem(item):
    try:
        item = item.replace(" ", "%")
        driver = init_driver()
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
        driver = init_driver()
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
            
        item_title = item_title.text.strip()  # Используем полное название товара
        print(f"Found product title: {item_title}")

        # Проверяем кэш перед выполнением запросов
        cached_reviews = await get_cached_reviews(item_title)
        if cached_reviews:
            print("Using cached reviews")
            reviews = []
            if cached_reviews.get('wb_reviews'):
                reviews.extend(cached_reviews['wb_reviews'])
            if cached_reviews.get('ozon_reviews'):
                reviews.extend(cached_reviews['ozon_reviews'])
            if cached_reviews.get('yandex_reviews'):
                reviews.extend(cached_reviews['yandex_reviews'])
            print(f"Found {len(reviews)} cached reviews")
            return reviews

        print("Fetching reviews from marketplaces...")
        
        # Используем asyncio.gather для параллельного выполнения запросов
        wb_reviews, ozon_reviews = await asyncio.gather(
            asyncio.to_thread(findRequiredItemFromWb, item_title),
            asyncio.to_thread(findRequiredItemFromOzon, item_title)
        )
        
        print(f"Found {len(wb_reviews) if wb_reviews else 0} WB reviews and {len(ozon_reviews) if ozon_reviews else 0} Ozon reviews")
        
        # Сохраняем отзывы в кэш с правильным разделением
        await cache_reviews(
            item_title=item_title,  # Используем полное название товара
            user_query=user_query,  # Сохраняем оригинальный запрос пользователя
            product_url=url,
            wb_reviews=wb_reviews if wb_reviews else [],
            ozon_reviews=ozon_reviews if ozon_reviews else [],
            yandex_reviews=[]  # Пока нет отзывов с Яндекс.Маркета
        )

        # Объединяем отзывы для возврата
        reviews = []
        if wb_reviews:
            reviews.extend(wb_reviews)
        if ozon_reviews:
            reviews.extend(ozon_reviews)

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

# if __name__ == "__main__":
#     findRequiredItemOnMarketplaces("https://www.wildberries.ru/catalog/34939243/detail.aspx")