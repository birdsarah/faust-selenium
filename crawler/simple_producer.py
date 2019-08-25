import uuid

from urllib.parse import quote

from app import (
    app,
    crawl_request_topic,
    CrawlRequest,
    Session,
)
from datasaver_db import DBCrawlRequest


simple_request_topic = app.topic('simple_request')


@app.agent(simple_request_topic)
async def crawl_request(requests):
    async for request in requests:
        url = quote(request.get('url', 'http://www.google.com'), safe=":/?=")
        req = CrawlRequest(id=str(uuid.uuid4()), url=url)
        print(f'Sending Request: {req.url}')
        session = Session()
        request = DBCrawlRequest(id=req.id, url=req.url)
        session.add(request)
        session.commit()
        session.close()

        await crawl_request_topic.send(value=req)
