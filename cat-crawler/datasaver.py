from app import (
    app,
    crawl_result_topic,
    crawl_log_topic,
)


@app.agent(crawl_result_topic)
async def datasaver(crawl_results):
    async for crawl_result in crawl_results:
        print(f'Receiving Result: {crawl_result.id} {crawl_result.success}')


@app.agent(crawl_log_topic)
async def log_datasaver(logs):
    async for log in logs:
        print(f'Receiving Log: {log.log}')
