import datetime
import os
import pytz
import time
import uuid

from concurrent.futures import ThreadPoolExecutor
from functools import partial
from selenium.common.exceptions import WebDriverException, TimeoutException
from urllib import parse

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
thread_pool = ThreadPoolExecutor(max_workers=1)


def do_crawl(driver, url):
    exceptions = []
    driver.set_page_load_timeout(TIME_OUT)
    try:
        tab_restart_browser(driver)
        driver.get(url)
        # Sleep after get returns (for a little longer than dwell time to
        # make sure all messages in time frame appear)
        time.sleep(DWELL_TIME_SECONDS * 1.3)
        success = True
        failure_type = ''
        message = ''
    except TimeoutException as e:
        exceptions.append(e)
        success = False
        failure_type = 'timeout'
        message = e.msg
    except WebDriverException as e:
        exceptions.append(e)
        success = False
        failure_type = 'webdriver'
        message = e.msg
        if message.startswith('Reached error page:'):
            try:
                parsed = parse.urlparse(message.replace('Reached error page:', ''))
                qs = parse.parse_qs(parsed.query)
                failure_type = f'{parsed.path.strip()}:{qs["e"][0]}'
            except:  # noqa
                # OK if we can't get out this extra detail
                pass
    finally:
        # How much problem that this isn't defensive?
        close_modals(driver)
        close_other_windows(driver)
        driver.quit()
    return success, failure_type, message, exceptions


@app.agent(crawl_request_topic)
async def crawl(crawl_requests):
    async for crawl_request in crawl_requests:
        print(f'Receiving Request: {crawl_request.url}')
        visit_id = (uuid.uuid4().int & (1 << 53) - 1) - 2**52
        driver, logs = await app.loop.run_in_executor(
            thread_pool,
            partial(
                get_driver,
                visit_id=visit_id,
                crawl_id=crawl_request.crawl_id,
                ws_port=WS_PORT,
            )
        )
        for log in logs:
            logger.info(log)
        success, failure_type, message, exceptions = await app.loop.run_in_executor(
            thread_pool,
            partial(
                do_crawl,
                driver=driver,
                url=crawl_request.url
            )
        )
        for e in exceptions:
            logger.exception(e)
        result = CrawlResult(
            request_id=crawl_request.request_id,
            visit_id=visit_id,
            url=crawl_request.url,
            success=success,
            time_stamp=str(datetime.datetime.now(pytz.utc)),
            failure_type=failure_type,
            message=message,
        )
        await crawl_result_topic.send(value=result)
