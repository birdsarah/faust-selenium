import datetime
import pytz
import time

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


@app.agent(crawl_request_topic)
async def crawl(crawl_requests):
    async for crawl_request in crawl_requests:
        print(f'Receiving Request: {crawl_request.url}')
        driver = get_driver(crawl_request.visit_id, crawl_request.crawl_id)
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
            visit_id=crawl_request.visit_id,
            success=success,
            time_stamp=str(datetime.datetime.now(pytz.utc))
        )
        await crawl_result_topic.send(value=result)
