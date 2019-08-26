import asyncio
import io
import json
import logging
import time
import traceback

import faust


# ---------------------------------------------------------------------
# Faust Records
# ---------------------------------------------------------------------

# TODO I think CrawlRequest should have a timestamp.
class CrawlRequest(faust.Record, serializer='json'):
    visit_id: str
    crawl_id: str
    url: str


class CrawlResult(faust.Record, serializer='json'):
    visit_id: str
    success: bool


class CrawlLog(faust.Record, serializer='json'):
    log: str


class WebExtStart(faust.Record, serializer='json'):
    visit_id: str
    crawl_id: str


class WebExtJavascript(faust.Record, serializer='json'):
    top_level_url: str
    document_url: str
    script_url: str

    crawl_id: str
    visit_id: str

    extension_session_uuid: str
    event_ordinal: int
    page_scoped_event_ordinal: int
    window_id: int
    tab_id: int
    frame_id: int
    script_line: str
    script_col: str
    func_name: str
    script_loc_eval: str
    call_stack: str
    symbol: str
    operation: str
    value: str
    time_stamp: str
    incognito: int
    arguments: str = ''  # Signifies optional


# ---------------------------------------------------------------------
# Setup Logging
# ---------------------------------------------------------------------

class KafkaLogHandler(logging.StreamHandler):

    async def send_log_to_kafka(self, log):
        await crawl_log_topic.send(value=CrawlLog(log=log))

    def emit(self, record):
        log = self.format(record)
        asyncio.ensure_future(self.send_log_to_kafka(log))

    def formatException(self, ei):
        # https://github.com/python/cpython/blob/3.7/Lib/logging/__init__.py#L554
        sio = io.StringIO()
        tb = ei[2]
        traceback.print_exception(ei[0], ei[1], tb, None, sio)
        s = sio.getvalue()
        sio.close()
        if s[-1:] == "\n":
            s = s[:-1]
        return s

    def format(self, record):
        # Make a json log, derived from:
        # https://github.com/python/cpython/blob/3.7/Lib/logging/__init__.py#L595
        timestamp = time.strftime(
            '%Y-%m-%d %H:%M:%S',
            time.localtime(record.created)
        )
        log = {
            'timestamp': timestamp,
            'msecs': record.msecs,
            'level': record.levelname,
            'name': record.name,
            'message': record.getMessage()
        }
        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            log['exception'] = record.exc_text
        if record.stack_info:
            log['stack'] = record.stack_info
        return json.dumps(log)


# ---------------------------------------------------------------------
# Set-up global state
# ---------------------------------------------------------------------

# App
APPNAME = 'openwpm'
BROKER = 'kafka://127.0.0.1:9092'
app = faust.App(APPNAME, broker=BROKER)
crawl_request_topic = app.topic('crawl-request', value_type=CrawlRequest)
crawl_request_log_topic = app.topic('crawl-request-log', value_type=CrawlRequest)
crawl_result_topic = app.topic('crawl-result', value_type=CrawlResult)
crawl_log_topic = app.topic('crawl-log', value_type=CrawlLog)
webext_start_topic = app.topic('webext-start', value_type=WebExtStart)
webext_javascript_topic = app.topic('webext-javascript', value_type=WebExtJavascript)

# Logging
logger = logging.getLogger('crawler')
logger.addHandler(KafkaLogHandler())
