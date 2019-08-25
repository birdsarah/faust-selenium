import json

from app import (
    app,
    crawl_result_topic,
    crawl_log_topic,
    Session,
)
from datasaver_db import (
    DBCrawlResult,
    DBLog,
    DBJavascript,
)


def atomic_add(item):
    session = Session()
    session.add(item)
    session.commit()
    session.close()


@app.agent(crawl_result_topic)
async def crawl_result_to_sql(crawl_results):
    async for crawl_result in crawl_results:
        result = DBCrawlResult(
            id=crawl_result.id[0],  # Why is this in a list?
            request_id=crawl_result.request_id,
            url=crawl_result.url,
            success=crawl_result.success
        )
        atomic_add(result)


@app.agent(crawl_log_topic)
async def logs_to_sql(logs):
    async for log in logs:
        # print(f'Receiving Log: {log.log}')
        log = json.loads(log.asdict()['log'])
        db_log = DBLog(**log)
        atomic_add(db_log)
