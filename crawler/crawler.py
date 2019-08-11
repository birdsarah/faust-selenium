import asyncio
import time
import uuid

from selenium.common.exceptions import WebDriverException

from app import (
    app,
    crawl_request_topic,
    crawl_result_topic,
    CrawlResult,
    logger
)
from geckodriver_log_reader import tail_F
from browser_setup import LOG_FILE, get_driver


@app.agent(crawl_request_topic)
async def crawl(crawl_requests):
    # Do a crawl for each crawl request
    async for crawl_request in crawl_requests:
        print(f'Receiving Request: {crawl_request.url}')

        # Do a crawl
        driver = get_driver()
        crawl_result_id = str(uuid.uuid4()),
        try:
            driver.get(crawl_request.url)
            time.sleep(60)
            success = True
        except WebDriverException as e:
            logger.exception(e)
            success = False
        finally:
            driver.close()

        result = CrawlResult(
            id=crawl_result_id,
            request_id=crawl_request.id,
            url=crawl_request.url,
            success=success,
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
