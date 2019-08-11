import re
import uuid

from urllib.parse import quote

from app import (
    app,
    crawl_request_topic,
    CrawlRequest,
)


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

        url = quote(grouped[1], safe=":/")
        req = CrawlRequest(id=str(uuid.uuid4()), url=url)
        print(f'Sending Request: {req.url}')
        await crawl_request_topic.send(value=req)
