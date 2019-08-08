import time
import uuid

from selenium.common.exceptions import WebDriverException
from selenium import webdriver

from app import (
    app,
    crawl_request_topic,
    crawl_result_topic,
    CrawlResult,
    logger
)


@app.agent(crawl_request_topic)
async def crawl(crawl_requests):
    async for crawl_request in crawl_requests:
        print(f'Receiving Request: {crawl_request.url}')

        # Do a crawl
        driver = webdriver.Firefox()
        try:
            driver.get(crawl_request.url)
            time.sleep(2)
        except WebDriverException as e:
            logger.exception(e)
        finally:
            driver.close()

        result = CrawlResult(
            id=str(uuid.uuid4()),
            request_id=crawl_request.id,
            url=crawl_request.url,
            success=True
        )
        await crawl_result_topic.send(value=result)
