import asyncio
import uuid

from app import (
    app,
    crawl_request_topic,
    crawl_result_topic,
    CrawlResult,
    logger
)


@app.agent(crawl_request_topic)
async def crawl(crawl_requests):
    async for crawl_request in crawl_requests:
        print(f'Receiving Request: {crawl_request.url}')
        result = CrawlResult(
            id=str(uuid.uuid4()),
            request_id=crawl_request.id,
            url=crawl_request.url,
            success=True
        )
        await asyncio.sleep(0.2)
        logger.info(f'THIS IS A LOG: Sending Result: {result.id}')
        await crawl_result_topic.send(value=result)
