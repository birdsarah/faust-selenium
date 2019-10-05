import csv
import datetime
import pytz
import uuid

from urllib.parse import quote

from app import (
    APPNAME,
    app,
    crawl_request_topic,
    crawl_request_log_topic,
    CrawlRequest,
)

CRAWL_ID = APPNAME

@app.task
async def producer():
    with open('../lists/alexatop1k.csv', 'r') as f:
        reader = csv.reader(f)
        sites = [item for sublist in list(reader) for item in sublist]

    sites = sites[0:100]
    for u in sites:
        url = quote(f'http://{u}', safe=":/?=")
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
