from selenium.common.exceptions import WebDriverException
from selenium import webdriver
import time


def crawl(url):
    driver = webdriver.Firefox()
    try:
        driver.get(url)
        time.sleep(2)
    except WebDriverException as e:
        print(e)
    finally:
        driver.close()


if __name__ == '__main__':
    crawl('http://example.com')
