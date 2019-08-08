import asyncio
import os
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
from geckodriver_log_reader import tail_F

# TODO
# - Work with command line argument LOG FILE
LOG_FILE = os.environ.get('GECKODRIVER_LOG_FILE', 'geckodriver.log')


@app.agent(crawl_request_topic)
async def crawl(crawl_requests):
    # Do a crawl for each crawl request
    async for crawl_request in crawl_requests:
        print(f'Receiving Request: {crawl_request.url}')

        # Do a crawl
        driver = webdriver.Firefox(service_log_path=LOG_FILE)
        try:
            driver.get(crawl_request.url)
            time.sleep(1)
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


@app.task
async def geckodriver_log_reader():
    # On startup start tailing the geckodriver log file and logging new lines
    for line in tail_F(LOG_FILE):
        if line != '':
            logger.info(f'GECKODRIVER {line}')
        # Throttle the output so things don't go too fast. Seems fine.
        await asyncio.sleep(0.2)
