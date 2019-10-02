import datetime
import os
import pytz
import time
import uuid

from selenium.common.exceptions import WebDriverException, TimeoutException

from app import (
    MANAGER_PARAMS,
    app,
    crawl_request_topic,
    crawl_result_topic,
    CrawlResult,
    logger
)
from browser_setup import get_driver
from browser_commands import (
    tab_restart_browser,
    close_other_windows,
    close_modals
)

DWELL_TIME_SECONDS = MANAGER_PARAMS['dwell_time']
TIME_OUT = MANAGER_PARAMS.get('timeout', 60)
WS_PORT = int(os.environ.get('WS_PORT', 7799))


@app.agent(crawl_request_topic)
async def crawl(crawl_requests):
    async for crawl_request in crawl_requests:
        print(f'Receiving Request: {crawl_request.url}')
        visit_id = (uuid.uuid4().int & (1 << 53) - 1) - 2**52
        driver = get_driver(
            visit_id=visit_id,
            crawl_id=crawl_request.crawl_id,
            ws_port=WS_PORT,
        )
        driver.set_page_load_timeout(TIME_OUT)
        tab_restart_browser(driver)
        try:
            driver.get(crawl_request.url)
            # Sleep after get returns
            time.sleep(DWELL_TIME_SECONDS)
            logger.info("Sleep complete")
            success = True
        except (WebDriverException, TimeoutException) as e:
            logger.exception(e)
            success = False
        finally:
            close_modals(driver)
            close_other_windows(driver)
            driver.quit()
        result = CrawlResult(
            request_id=crawl_request.request_id,
            visit_id=visit_id,
            success=success,
            time_stamp=str(datetime.datetime.now(pytz.utc))
        )
        await crawl_result_topic.send(value=result)
