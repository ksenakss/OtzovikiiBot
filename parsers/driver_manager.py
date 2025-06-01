import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Создаем глобальные драйверы для разных задач
search_driver = None
wb_reviews_driver = None
ozon_reviews_driver = None
yandex_market_driver = None
options = uc.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
chrome_driver_path = "C:\\Users\\Admin\\PycharmProjects\\OtzovikiiBot\\chromedriver.exe"
service = Service(chrome_driver_path)

def init_search_driver():
    print("init_search_driver")
    global search_driver
    print("search_driver1")
    if not search_driver:
        search_driver = uc.Chrome(service=Service(chrome_driver_path), headless=False, use_subprocess=False)
        # search_driver = webdriver.Chrome(service=service)
    print("search_driver2")
    return search_driver

def init_wb_reviews_driver():
    global wb_reviews_driver
    if not wb_reviews_driver:
        wb_reviews_driver = uc.Chrome(service=Service(chrome_driver_path), headless=False, use_subprocess=False)
        # wb_reviews_driver = webdriver.Chrome(service=service)
    return wb_reviews_driver

def init_ozon_reviews_driver():
    global ozon_reviews_driver
    if not ozon_reviews_driver:
        ozon_reviews_driver = uc.Chrome(service=Service(chrome_driver_path), headless=False, use_subprocess=False)
        # ozon_reviews_driver = webdriver.Chrome(service=service)
    return ozon_reviews_driver

def init_yandex_market_driver():
    global yandex_market_driver
    if not yandex_market_driver:
        yandex_market_driver = uc.Chrome(service=Service(chrome_driver_path), headless=False, use_subprocess=False)
        # yandex_market_driver = webdriver.Chrome(service=service)
    return yandex_market_driver

def cleanup():
    global search_driver, wb_reviews_driver, ozon_reviews_driver, yandex_market_driver
    if search_driver:
        search_driver.quit()
        search_driver = None
    if wb_reviews_driver:
        wb_reviews_driver.quit()
        wb_reviews_driver = None
    if ozon_reviews_driver:
        ozon_reviews_driver.quit()
        ozon_reviews_driver = None
    if yandex_market_driver:
        yandex_market_driver.quit()
        yandex_market_driver = None