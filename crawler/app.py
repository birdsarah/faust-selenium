import asyncio
import io
import json
import logging
import os
import time
import traceback

import faust

BROWSER_PARAMS_FILE = os.environ.get('BROWSER_PARAMS_FILE', 'browser_params.json')
manager_params_file = os.environ.get('MANAGER_PARAMS_FILE', 'manager_params.json')
with open(manager_params_file, 'r') as f:
    MANAGER_PARAMS = json.loads(f.read())
APPNAME = MANAGER_PARAMS['crawl_name']
BROKER = MANAGER_PARAMS['kafka_broker']

# This also needs to be set in the kafka configuration
# https://stackoverflow.com/questions/21020347/how-can-i-send-large-messages-with-kafka-over-15mb
MAX_MESSAGE_SIZE = 1024 * 1024 * 40


# ---------------------------------------------------------------------
# Faust Records
# ---------------------------------------------------------------------

class CrawlRequest(faust.Record, serializer='json'):
    request_id: str
    crawl_id: str
    url: str
    time_stamp: str


class CrawlResult(faust.Record, serializer='json'):
    request_id: str
    visit_id: str
    success: bool
    time_stamp: str


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

    # Optional fields
    window_id: int = -1
    arguments: str = ''  # Signifies optional


class WebExtJavascriptCookie(faust.Record, serializer='json'):
    crawl_id: str
    visit_id: str
    time_stamp: str

    record_type: str
    change_cause: str
    extension_session_uuid: str
    event_ordinal: int
    expiry: str
    is_http_only: int
    is_host_only: int
    is_session: int
    host: str
    is_secure: int
    name: str
    path: str
    value: str
    same_site: str
    first_party_domain: str
    store_id: str


class WebExtNavigation(faust.Record, serializer='json'):
    crawl_id: str
    visit_id: str

    transition_qualifiers: str
    transition_type: str
    committed_event_ordinal: int
    committed_time_stamp: str

    incognito: int
    extension_session_uuid: str
    tab_id: int
    frame_id: int
    window_width: int
    window_height: int
    window_type: str
    tab_width: int
    tab_height: int
    tab_cookie_store_id: str
    uuid: str
    url: str

    # Optional fields
    window_id: int = -1
    process_id: int = -1
    tab_opener_tab_id: int = -1
    before_navigate_event_ordinal: int = -1
    before_navigate_time_stamp: str = ''
    parent_frame_id: int = -1


class WebExtHttpRequest(faust.Record, serializer='json'):
    crawl_id: str
    visit_id: str
    time_stamp: str

    incognito: int
    extension_session_uuid: str
    event_ordinal: int
    tab_id: int
    frame_id: int
    parent_frame_id: int
    request_id: str

    url: str
    top_level_url: str
    method: str
    referrer: str
    headers: str
    is_XHR: int
    is_full_page: int
    is_frame_load: int
    triggering_origin: str
    loading_origin: str
    loading_href: str
    resource_type: str
    frame_ancestors: str

    # Optional fields
    window_id: int = -1
    post_body: str = ''
    post_body_raw: str = ''


class WebExtHttpResponse(faust.Record, serializer='json'):
    crawl_id: str
    visit_id: str
    time_stamp: str

    incognito: int
    extension_session_uuid: str
    event_ordinal: int
    tab_id: int
    frame_id: int
    request_id: str

    is_cached: int
    url: str
    method: str
    headers: str
    location: str

    # Optional fields
    window_id: int = -1
    content_hash: str = ''
    response_status: str = ''
    response_status_text: str = ''


class WebExtHttpResponseContent(faust.Record, serializer='json'):
    content_hash: str
    b64: str  # This gets decoded and turned into content


class WebExtHttpRedirect(faust.Record, serializer='json'):
    crawl_id: str
    visit_id: str
    time_stamp: str

    incognito: int
    extension_session_uuid: str
    event_ordinal: int
    tab_id: int
    frame_id: int
    old_request_id: str
    new_request_id: str
    old_request_url: str
    new_request_url: str

    # Optional fields
    window_id: int = -1
    response_status: str = ''
    response_status_text: str = ''


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
app = faust.App(APPNAME, broker=BROKER, producer_max_request_size=MAX_MESSAGE_SIZE)
crawl_request_topic = app.topic(f'{APPNAME}-crawl-request', value_type=CrawlRequest)
crawl_result_topic = app.topic(f'{APPNAME}-crawl-result', value_type=CrawlResult)
crawl_log_topic = app.topic(f'{APPNAME}-crawl-log', value_type=CrawlLog)
webext_start_topic = app.topic(f'{APPNAME}-webext-start', value_type=WebExtStart)
webext_javascript_topic = app.topic(f'{APPNAME}-webext-javascript', value_type=WebExtJavascript)
webext_javascript_cookie_topic = app.topic(f'{APPNAME}-webext-javascript-cookie', value_type=WebExtJavascriptCookie)
webext_navigation_topic = app.topic(f'{APPNAME}-webext-navigation', value_type=WebExtNavigation)
webext_http_request_topic = app.topic(f'{APPNAME}-webext-http-request', value_type=WebExtHttpRequest)
webext_http_response_topic = app.topic(f'{APPNAME}-webext-http-response', value_type=WebExtHttpResponse)
webext_http_response_content_topic = app.topic(f'{APPNAME}-webext-http-response-content', value_type=WebExtHttpResponseContent)
webext_http_redirect_topic = app.topic(f'{APPNAME}-webext-http-redirect', value_type=WebExtHttpRedirect)

# Logging
logger = logging.getLogger('crawler')
logger.addHandler(KafkaLogHandler())
