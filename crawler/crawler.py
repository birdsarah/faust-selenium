import datetime
import json
import pytz
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
from browser_setup import get_driver

with open('manager_params.json', 'r') as f:
    manager_params = json.loads(f.read())
DWELL_TIME_SECONDS = manager_params['dwell_time']


@app.agent(crawl_request_topic)
async def crawl(crawl_requests):
    async for crawl_request in crawl_requests:
        print(f'Receiving Request: {crawl_request.url}')
        driver = get_driver(crawl_request.visit_id, crawl_request.crawl_id)

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
            visit_id=crawl_request.visit_id,
            success=success,
            time_stamp=str(datetime.datetime.now(pytz.utc))
        )
        await crawl_result_topic.send(value=result)
