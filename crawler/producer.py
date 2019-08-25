import re
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
    with open('tranco_10k_alexa_10k_union.unlimited_depth_max_10_links.ranked.csv', 'r') as f:
        data = f.read()
    data = data[0:10]  # Just testing for now

    regex = r"(\d+),(.+)"
    matches = re.finditer(regex, data, re.MULTILINE)
    for match in matches:
        grouped = match.groups()
        assert len(grouped) == 2

        url = quote(grouped[1], safe=":/?=")
        visit_id = (uuid.uuid4().int & (1 << 53) - 1) - 2**52
        req = CrawlRequest(url=url, visit_id=visit_id, crawl_id=CRAWL_ID)

        print(f'Sending Request: {req.url}')
        await crawl_request_log_topic.send(value=req)
        await crawl_request_topic.send(value=req)
