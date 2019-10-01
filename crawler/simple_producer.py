import datetime
import pytz
import uuid


from urllib.parse import quote

from app import (
    app,
    crawl_request_topic,
    crawl_request_log_topic,
    CrawlRequest,
)


simple_request_topic = app.topic('simple_request')


@app.agent(simple_request_topic)
async def crawl_request(requests):
    async for request in requests:
        url = quote(request.get('url', 'http://www.google.com'), safe=":/?=")
        visit_id = (uuid.uuid4().int & (1 << 53) - 1) - 2**52
        req = CrawlRequest(
            url=url,
            visit_id=visit_id,
            crawl_id='simple',
            time_stamp=str(datetime.datetime.now(pytz.utc))
        )
        print(f'Sending Request: {req.url}')
        await crawl_request_log_topic.send(value=req)
        await crawl_request_topic.send(value=req)
