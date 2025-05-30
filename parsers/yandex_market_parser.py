from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from parsers.driver_manager import init_yandex_market_driver

def convert_to_reviews_url(product_url):
    try:
        parts = product_url.split('/')
        product_id = parts[-1].split('?')[0]
        sku = None
        unique_id = None
        
        params = product_url.split('?')[1].split('&')
        for param in params:
            if param.startswith('sku='):
                sku = param.split('=')[1]
            elif param.startswith('uniqueId='):
                unique_id = param.split('=')[1]
        
        if not sku or not unique_id:
            return None
            
        reviews_url = f"https://market.yandex.ru/product--{product_id}/reviews?sku={sku}&uniqueId={unique_id}&businessReviews=1"
        return reviews_url
    except Exception as e:
        print(f"Error converting URL: {str(e)}")
        return None

def findRequiredItemFromYandex(item_title):
    driver = None
    reviews = []
    try:
        driver = init_yandex_market_driver()
        print(f"Starting Yandex Market search for: {item_title}")
        driver.get(f"https://market.yandex.ru/search?text={item_title}")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-zone-name='productSnippet']"))
            )
        except Exception as e:
            print(f"Timeout waiting for Yandex Market search results: {str(e)}")
            return reviews
        page_html = driver.page_source
        soup = BeautifulSoup(page_html, "html.parser")
        products = soup.find_all("div", attrs={"data-zone-name": "productSnippet"})
        reviews_count = []
        product_urls = []
        
        for product in products[13:]:
            title_element = product.find("span", class_="ds-text_lineClamp_2")
            if not title_element:
                continue
                
            title = title_element.text.strip()
            try:
                link_element = product.find("a", {"data-baobab-name": "title"})
                if link_element and 'href' in link_element.attrs:
                    product_url = "https://market.yandex.ru" + link_element['href']
                    product_urls.append(product_url)
                rating_element = product.find("div", {"data-baobab-name": "rating"})
                if rating_element:
                    reviews_span = rating_element.find("span", class_="ds-text_text_reg")
                    if reviews_span:
                        reviews_text = reviews_span.text.strip()
                        reviews_num = ''.join(filter(str.isdigit, reviews_text))
                        reviews_count.append((title, int(reviews_num)))
                    else:
                        reviews_count.append((title, 0))
                else:
                    reviews_count.append((title, 0))
            except:
                reviews_count.append((title, 0))

        if reviews_count:
            most_reviewed_index = reviews_count.index(max(reviews_count, key=lambda x: x[1]))
            print(most_reviewed_index)
            if most_reviewed_index < len(product_urls):
                product_url = product_urls[most_reviewed_index]
                reviews_url = convert_to_reviews_url(product_url)
                if reviews_url:
                    print(f"Found product with {reviews_count[most_reviewed_index][1]} reviews yandex")
                    reviews = parseReviewsFromYandex(reviews_url)
                else:
                    print("Could not convert product URL to reviews URL")
            else:
                print("Product URL not found for the most reviewed item")
        else:
            print("No products found with reviews")
            
    except Exception as e:
        print(f"Ошибка при поиске товара на Yandex Market: {str(e)}")
    return reviews

def parseReviewsFromYandex(url):
    reviews = []
    try:
        driver = init_yandex_market_driver()
        print(f"Parsing Yandex Market reviews from: {url}")
        driver.get(url)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-baobab-name='review']"))
            )
        except Exception as e:
            print(f"Timeout waiting for reviews: {str(e)}")
            return reviews
        page_html = driver.page_source
        soup = BeautifulSoup(page_html, "html.parser")
        for _ in range(2):
            current_reviews = len(soup.find_all("div", {"data-baobab-name": "review"}))
            
            driver.execute_script("window.scrollBy(0, 5000);")
            
            try:
                WebDriverWait(driver, 5).until(
                    lambda d: len(BeautifulSoup(d.page_source, "html.parser").find_all("div", {"data-baobab-name": "review"})) > current_reviews
                )
            except:
                pass
                
            time.sleep(2)
        page_html = driver.page_source
        soup = BeautifulSoup(page_html, "html.parser")
        review_blocks = soup.find_all("div", {"data-baobab-name": "review"})
        
        for block in review_blocks:
            review_text = ""
            pros = block.find("span", {"data-auto": "review-pro"})
            cons = block.find("span", {"data-auto": "review-contra"})
            comment = block.find("span", {"data-auto": "review-comment"})
            
            if pros:
                review_text += f"Достоинства: {pros.text.strip()}\n"
            if cons:
                review_text += f"Недостатки: {cons.text.strip()}\n"
            if comment:
                review_text += f"Комментарий: {comment.text.strip()}"
            
            if review_text.strip():
                reviews.append(review_text.strip())

        print(f"Found {len(reviews)} reviews on Yandex Market")
    except Exception as e:
        print(f"Ошибка при парсинге отзывов: {str(e)}")
    return reviews