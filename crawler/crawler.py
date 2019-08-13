import json
import uuid

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException

from app import (
    app,
    crawl_request_topic,
    crawl_result_topic,
    CrawlResult,
    logger
)
from browser_setup import LOG_FILE, get_driver

manager_params = json.loads(open('manager_params.json').read())
DWELL_TIME_SECONDS = manager_params['dwell_time']
CRAWL_ID = (uuid.uuid4().int & (1 << 32) - 1) - 2**31


@app.agent(crawl_request_topic)
async def crawl(crawl_requests):
    # Do a crawl for each crawl request
    async for crawl_request in crawl_requests:
        print(f'Receiving Request: {crawl_request.url}')

        # Do a crawl
        visit_id = (uuid.uuid4().int & (1 << 53) - 1) - 2**52
        crawl_result_id = str(uuid.uuid4()),

        driver = get_driver(visit_id, CRAWL_ID)

        try:
            driver.get(crawl_request.url)
            try:
                wait = WebDriverWait(driver, DWELL_TIME_SECONDS)
                # We never expect this to happen, so should get x seconds wait
                wait.until(EC.title_is(uuid.uuid4()), "Successful waiting completed")
            except TimeoutException as e:
                logger.info(e)
                success = True
        except WebDriverException as e:
            logger.exception(e)
            success = False
        finally:
            driver.quit()

        result = CrawlResult(
            id=crawl_result_id,
            request_id=crawl_request.id,
            url=crawl_request.url,
            success=success,
        )
        await crawl_result_topic.send(value=result)
