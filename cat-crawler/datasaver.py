from app import (
    app,
    crawl_result_topic,
)


@app.agent(crawl_result_topic)
async def datasaver(crawl_results):
    async for crawl_result in crawl_results:
        print(f'Receiving Result: {crawl_result.id} {crawl_result.success}')
