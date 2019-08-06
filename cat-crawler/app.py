import faust
import datetime


class CrawlRequest(faust.Record, serializer='json'):
    id: str
    url: str


class CrawlResult(faust.Record, serializer='json'):
    id: str
    request_id: str
    url: str
    success: bool


class CrawlLog(faust.Record, serializer='json'):
    result_id: str
    timestamp: datetime
    log: str


app = faust.App('crawler', broker='kafka://localhost:9092')
crawl_request_topic = app.topic('crawl-request', value_type=CrawlRequest)
crawl_result_topic = app.topic('crawl-result', value_type=CrawlResult)
crawl_log_topic = app.topic('crawl-log', value_type=CrawlLog)