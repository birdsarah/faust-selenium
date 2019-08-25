import json

from app import (
    app,
    crawl_result_topic,
    crawl_request_log_topic,
    crawl_log_topic,
    webext_start_topic,
    Session,
)
from datasaver_db import (
    DBCrawlResult,
    DBCrawlRequest,
    DBLog,
    # DBJavascript,
    DBWebExtStart,
)


def atomic_add(item):
    session = Session()
    session.add(item)
    session.commit()
    session.close()


@app.agent(crawl_request_log_topic)
async def crawl_request_to_sql(crawl_requests):
    async for crawl_request in crawl_requests:
        r = DBCrawlRequest(**crawl_request.asdict())
        atomic_add(r)


@app.agent(crawl_result_topic)
async def crawl_result_to_sql(crawl_results):
    async for crawl_result in crawl_results:
        r = DBCrawlResult(**crawl_result.asdict())
        atomic_add(r)


@app.agent(webext_start_topic)
async def webext_start_to_sql(starts):
    async for start in starts:
        r = DBWebExtStart(**start.asdict())
        atomic_add(r)


@app.agent(crawl_log_topic)
async def logs_to_sql(logs):
    async for log in logs:
        # Extract log body from log kafka message
        log_body = json.loads(
            log.asdict()['log']
        )
        db_log = DBLog(**log_body)
        atomic_add(db_log)
