import datetime
import json
import pytz
import uuid

from urllib.parse import quote

from app import (
    app,
    crawl_request_topic,
    crawl_request_log_topic,
    CrawlRequest,
)

CRAWL_ID = (uuid.uuid4().int & (1 << 32) - 1) - 2**31


@app.task
async def producer():
    url_list = json.load(open('sample_of_js_cookies_sites_200.csv', 'r'))
    for u in url_list:
        url = quote(u, safe=":/?=")
        request_id = (uuid.uuid4().int & (1 << 53) - 1) - 2**52
        req = CrawlRequest(
            url=url,
            request_id=request_id,
            crawl_id=CRAWL_ID,
            time_stamp=str(datetime.datetime.now(pytz.utc))
        )

        print(f'Sending Request: {req.url}')
        await crawl_request_log_topic.send(value=req)
        await crawl_request_topic.send(value=req)
