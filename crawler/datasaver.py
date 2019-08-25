from datetime import datetime  # noqa

from sqlalchemy import Column, Integer, Text, String, Boolean, ForeignKey, DateTime  # noqa
from sqlalchemy.engine import create_engine

from app import (
    app,
    crawl_result_topic,
    crawl_log_topic,
)
from datasaver_db import (
    Base,
    Session,
    DBCrawlResult,
    DBJavascript,
)

engine = create_engine('sqlite:///crawldata.db')

Base.metadata.bind = engine
Session.configure(bind=engine)
Base.metadata.create_all()

log_map = {
    'javascript': DBJavascript,
}


@app.agent(crawl_result_topic)
async def datasaver(crawl_results):
    async for crawl_result in crawl_results:
        session = Session()
        result = DBCrawlResult(
            id=crawl_result.id[0],  # why is this in a list?
            success=crawl_result.success
        )
        session.add(result)
        session.commit()
        session.close()
        print(f'Receiving Result: {crawl_result.id} {crawl_result.success}')


@app.agent(crawl_log_topic)
async def log_datasaver(logs):
    async for log in logs:
        print(dir(log))
        print(log.keys())
        print(f'Receiving Log: {log.log}')

