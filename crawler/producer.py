import csv
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

CRAWL_ID = (uuid.uuid4().int & (1 << 32) - 1) - 2**31


@app.task
async def producer():
    with open('alexatop1k.csv', 'r') as f:
        reader = csv.reader(f)
        sites = [item for sublist in list(reader) for item in sublist]

    sites = sites
    for u in sites:
        url = quote(f'http://{u}', safe=":/?=")
        visit_id = (uuid.uuid4().int & (1 << 53) - 1) - 2**52
        req = CrawlRequest(
            url=url,
            visit_id=visit_id,
            crawl_id=CRAWL_ID,
            time_stamp=str(datetime.datetime.now(pytz.utc))
        )

        print(f'Sending Request: {req.url}')
        await crawl_request_log_topic.send(value=req)
        await crawl_request_topic.send(value=req)
