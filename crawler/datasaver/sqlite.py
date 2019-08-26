import json

from sqlalchemy import Column, Integer, Text, String, Boolean, ForeignKey, DateTime  # noqa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import create_engine

from app import (
    app,
    crawl_result_topic,
    crawl_request_log_topic,
    crawl_log_topic,
    webext_start_topic,
    webext_javascript_topic,
    webext_javascript_cookie_topic,
    webext_navigation_topic,
    webext_http_request_topic,
    webext_http_response_topic,
    webext_http_redirect_topic,
)

Session = sessionmaker()
Base = declarative_base()


class DBCrawlRequest(Base):
    __tablename__ = 'crawl_requests'

    id = Column(Integer(), primary_key=True, auto_increment=True)
    visit_id = Column(String(256), nullable=False)
    crawl_id = Column(String(256), nullable=False)
    url = Column(Text(), nullable=False)


class DBCrawlResult(Base):
    __tablename__ = 'crawl_results'

    id = Column(Integer(), primary_key=True, auto_increment=True)
    visit_id = Column(String(256), nullable=False)
    success = Column(Boolean(), nullable=False)


class DBLog(Base):
    # The fields here should match those in KafkaLogHandler (app.py)
    __tablename__ = 'logs'
    id = Column(Integer(), primary_key=True, auto_increment=True)
    timestamp = Column(String(256), nullable=False)
    msecs = Column(Integer(), nullable=False)
    name = Column(Text(), nullable=False)
    level = Column(String(256), nullable=False)
    message = Column(Text(), nullable=False)
    exception = Column(Text())
    stack = Column(Text())


class DBWebExtStart(Base):
    __tablename__ = 'webext_starts'

    id = Column(Integer(), primary_key=True, auto_increment=True)
    visit_id = Column(String(256), nullable=False)
    crawl_id = Column(String(256), nullable=False)


class DBWebExtJavascript(Base):
    __tablename__ = 'javascript'

    id = Column(Integer(), primary_key=True, auto_increment=True)
    crawl_id = Column(String(256))
    visit_id = Column(String(256))
    time_stamp = Column(String(256))  # Parse?

    top_level_url = Column(Text())
    document_url = Column(Text())
    script_url = Column(Text())

    extension_session_uuid = Column(String(256))
    event_ordinal = Column(Integer())
    page_scoped_event_ordinal = Column(Integer())
    window_id = Column(Integer())
    tab_id = Column(Integer())
    frame_id = Column(Integer())
    script_line = Column(String(12))
    script_col = Column(String(12))
    func_name = Column(Text())
    script_loc_eval = Column(Text())
    call_stack = Column(Text())
    symbol = Column(String(256))
    operation = Column(String(12))
    incognito = Column(Integer())
    value = Column(Text())  # Max length?
    arguments = Column(Text())  # Parse?


class DBWebExtJavascriptCookie(Base):
    __tablename__ = 'javascript_cookies'

    id = Column(Integer(), primary_key=True, auto_increment=True)
    crawl_id = Column(String(256))
    visit_id = Column(String(256))
    time_stamp = Column(String(256))

    record_type = Column(String(256))
    change_cause = Column(String(256))
    extension_session_uuid = Column(String(256))
    event_ordinal = Column(Integer())
    expiry = Column(String(256))
    is_http_only = Column(Integer())
    is_host_only = Column(Integer())
    is_session = Column(Integer())
    host = Column(Text())
    is_secure = Column(Integer())
    name = Column(Text())
    path = Column(Text())
    value = Column(Text())
    same_site = Column(Text())
    first_party_domain = Column(Text())
    store_id = Column(Text())


class DBWebExtNavigation(Base):
    __tablename__ = 'navigations'

    id = Column(Integer(), primary_key=True, auto_increment=True)
    crawl_id = Column(String(256))
    visit_id = Column(String(256))

    before_navigate_event_ordinal = Column(Integer())
    before_navigate_time_stamp = Column(String(256))
    parent_frame_id = Column(Integer())

    transition_qualifiers = Column(Text())
    transition_type = Column(Text())
    committed_event_ordinal = Column(Integer())
    committed_time_stamp = Column(String(256))

    incognito = Column(Integer())
    extension_session_uuid = Column(String(256))
    process_id = Column(Integer())
    window_id = Column(Integer())
    tab_id = Column(Integer())
    tab_opener_tab_id = Column(Integer())
    frame_id = Column(Integer())
    window_width = Column(Integer())
    window_height = Column(Integer())
    window_type = Column(String(256))
    tab_width = Column(Integer())
    tab_height = Column(Integer())
    tab_cookie_store_id = Column(Text())
    uuid = Column(String(256))
    url = Column(Text())


class DBWebExtHttpRequest(Base):
    __tablename__ = 'http_requests'

    id = Column(Integer(), primary_key=True, auto_increment=True)
    crawl_id = Column(String(256))
    visit_id = Column(String(256))
    time_stamp = Column(String(256))

    extension_session_uuid = Column(String(256))
    event_ordinal = Column(Integer())
    window_id = Column(Integer())
    tab_id = Column(Integer())
    frame_id = Column(Integer())
    parent_frame_id = Column(Integer())
    request_id = Column(Integer())

    url = Column(Text())
    top_level_url = Column(Text())
    method = Column(String(256))
    referrer = Column(Text())
    post_body = Column(Text())
    post_body_raw = Column(Text())
    headers = Column(Text())
    is_XHR = Column(Integer())
    is_full_page = Column(Integer())
    is_frame_load = Column(Integer())
    triggering_origin = Column(Text())
    loading_origin = Column(Text())
    loading_href = Column(Text())
    resource_type = Column(String(256))
    frame_ancestors = Column(Text())


class DBWebExtHttpResponse(Base):
    __tablename__ = 'http_responses'

    id = Column(Integer(), primary_key=True, auto_increment=True)
    crawl_id = Column(String(256))
    visit_id = Column(String(256))
    time_stamp = Column(String(256))

    incognito = Column(Integer())
    extension_session_uuid = Column(String(256))
    event_ordinal = Column(Integer())
    window_id = Column(Integer())
    tab_id = Column(Integer())
    frame_id = Column(Integer())
    request_id = Column(Integer())

    is_cached = Column(Integer())
    url = Column(Text())
    method = Column(String(256))
    response_status = Column(String(256))
    response_status_text = Column(Text())
    headers = Column(Text())
    location = Column(Text())
    content_hash = Column(Text())


class DBWebExtHttpRedirect(Base):
    __tablename__ = 'http_redirects'

    id = Column(Integer(), primary_key=True, auto_increment=True)
    crawl_id = Column(String(256))
    visit_id = Column(String(256))
    time_stamp = Column(String(256))

    extension_session_uuid = Column(String(256))
    event_ordinal = Column(Integer())
    window_id = Column(Integer())
    tab_id = Column(Integer())
    frame_id = Column(Integer())
    old_request_id = Column(Integer())
    new_request_id = Column(Integer())
    old_request_url = Column(Text())
    new_request_url = Column(Text())

    response_status = Column(Text())
    response_status_text = Column(Text())


# Setup Database

with open('manager_params.json', 'r') as f:
    manager_params = json.loads(f.read())
DATABASE_NAME = manager_params['database_name']

engine = create_engine(f'sqlite:///{DATABASE_NAME}')
Base.metadata.bind = engine
Session.configure(bind=engine)
Base.metadata.create_all()


# Faust work to save data

def _atomic_add(item):
    session = Session()
    session.add(item)
    session.commit()
    session.close()


@app.agent(crawl_request_log_topic)
async def crawl_request_to_sql(crawl_requests):
    async for crawl_request in crawl_requests:
        r = DBCrawlRequest(**crawl_request.asdict())
        _atomic_add(r)


@app.agent(crawl_result_topic)
async def crawl_result_to_sql(crawl_results):
    async for crawl_result in crawl_results:
        r = DBCrawlResult(**crawl_result.asdict())
        _atomic_add(r)


@app.agent(crawl_log_topic)
async def logs_to_sql(logs):
    # TODO - make this only save for a specific user specified log-level
    async for log in logs:
        # Extract log body from log kafka message
        log_body = json.loads(
            log.asdict()['log']
        )
        db_log = DBLog(**log_body)
        _atomic_add(db_log)


@app.agent(webext_start_topic)
async def webext_start_to_sql(starts):
    async for start in starts:
        r = DBWebExtStart(**start.asdict())
        _atomic_add(r)


@app.agent(webext_javascript_topic)
async def webext_javascript_to_sql(stream):
    async for msg in stream:
        r = DBWebExtJavascript(**msg.asdict())
        _atomic_add(r)


@app.agent(webext_javascript_cookie_topic)
async def webext_javascript_cookie_to_sql(stream):
    async for msg in stream:
        r = DBWebExtJavascriptCookie(**msg.asdict())
        _atomic_add(r)


@app.agent(webext_navigation_topic)
async def webext_navigation_to_sql(stream):
    async for msg in stream:
        r = DBWebExtNavigation(**msg.asdict())
        _atomic_add(r)


@app.agent(webext_http_request_topic)
async def webext_http_request_to_sql(stream):
    async for msg in stream:
        r = DBWebExtHttpRequest(**msg.asdict())
        _atomic_add(r)


@app.agent(webext_http_response_topic)
async def webext_http_response_to_sql(stream):
    async for msg in stream:
        r = DBWebExtHttpResponse(**msg.asdict())
        _atomic_add(r)


@app.agent(webext_http_redirect_topic)
async def webext_http_redirect_to_sql(stream):
    async for msg in stream:
        r = DBWebExtHttpRedirect(**msg.asdict())
        _atomic_add(r)
