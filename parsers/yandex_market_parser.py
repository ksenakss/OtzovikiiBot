from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Настройка драйвера
driver_path = r'C:\Users\Admin\PycharmProjects\OtzovikiiBot\chromedriver.exe'
driver = webdriver.Chrome(executable_path=driver_path)  # Убедитесь, что у вас установлен драйвер Chrome
driver.get("https://market.yandex.ru/search?text=пылесос")

# Прокрутка вниз страницы
for _ in range(3):  # Прокручиваем 3 раза
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
    time.sleep(1)  # Ждем, чтобы контент успел загрузиться

# Скачивание HTML-кода страницы
html = driver.page_source

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
most_reviewed_product = max(reviews_count, key=lambda x: x[1])

print(f"Товар с наибольшим количеством отзывов: {most_reviewed_product[0]} с {most_reviewed_product[1]} отзывами.")

# Закрытие драйвера
driver.quit()
