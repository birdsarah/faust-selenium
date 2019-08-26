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
    crawl_id = Column(String(256), nullable=False)
    visit_id = Column(String(256), nullable=False)
    time_stamp = Column(String(256), nullable=False)  # Parse?

    top_level_url = Column(Text(), nullable=False)
    document_url = Column(Text(), nullable=False)
    script_url = Column(Text(), nullable=False)

    extension_session_uuid = Column(String(256), nullable=False)
    event_ordinal = Column(Integer(), nullable=False)
    page_scoped_event_ordinal = Column(Integer(), nullable=False)
    window_id = Column(Integer(), nullable=False)
    tab_id = Column(Integer(), nullable=False)
    frame_id = Column(Integer(), nullable=False)
    script_line = Column(String(12), nullable=False)
    script_col = Column(String(12), nullable=False)
    func_name = Column(Text(), nullable=False)
    script_loc_eval = Column(Text(), nullable=False)
    call_stack = Column(Text(), nullable=False)
    symbol = Column(String(256), nullable=False)
    operation = Column(String(12), nullable=False)
    incognito = Column(Integer(), nullable=False)
    value = Column(Text(), nullable=False)  # Max length?
    arguments = Column(Text(), nullable=False)  # Parse?


class DBWebExtJavascriptCookie(Base):
    __tablename__ = 'javascript_cookies'

    id = Column(Integer(), primary_key=True, auto_increment=True)
    crawl_id = Column(String(256), nullable=False)
    visit_id = Column(String(256), nullable=False)
    time_stamp = Column(String(256), nullable=False)

    record_type = Column(String(256), nullable=False)
    change_cause = Column(String(256), nullable=False)
    extension_session_uuid = Column(String(256), nullable=False)
    event_ordinal = Column(Integer(), nullable=False)
    expiry = Column(String(256), nullable=False)
    is_http_only = Column(Integer(), nullable=False)
    is_host_only = Column(Integer(), nullable=False)
    is_session = Column(Integer(), nullable=False)
    host = Column(Text(), nullable=False)
    is_secure = Column(Integer(), nullable=False)
    name = Column(Text(), nullable=False)
    path = Column(Text(), nullable=False)
    value = Column(Text(), nullable=False)
    same_site = Column(Text(), nullable=False)
    first_party_domain = Column(Text(), nullable=False)
    store_id = Column(Text(), nullable=False)


class DBWebExtNavigation(Base):
    __tablename__ = 'navigations'

    id = Column(Integer(), primary_key=True, auto_increment=True)
    crawl_id = Column(String(256), nullable=False)
    visit_id = Column(String(256), nullable=False)

    before_navigate_event_ordinal = Column(Integer(), nullable=False)
    before_navigate_time_stamp = Column(String(256), nullable=False)
    parent_frame_id = Column(Integer(), nullable=False)

    transition_qualifiers = Column(Text(), nullable=False)
    transition_type = Column(Text(), nullable=False)
    committed_event_ordinal = Column(Integer(), nullable=False)
    committed_time_stamp = Column(String(256), nullable=False)

    incognito = Column(Integer(), nullable=False)
    extension_session_uuid = Column(String(256), nullable=False)
    process_id = Column(Integer(), nullable=False)
    window_id = Column(Integer(), nullable=False)
    tab_id = Column(Integer(), nullable=False)
    tab_opener_tab_id = Column(Integer(), nullable=False)
    frame_id = Column(Integer(), nullable=False)
    window_width = Column(Integer(), nullable=False)
    window_height = Column(Integer(), nullable=False)
    window_type = Column(String(256), nullable=False)
    tab_width = Column(Integer(), nullable=False)
    tab_height = Column(Integer(), nullable=False)
    tab_cookie_store_id = Column(Text(), nullable=False)
    uuid = Column(String(256), nullable=False)
    url = Column(Text(), nullable=False)


class DBWebExtHttpRequest(Base):
    __tablename__ = 'http_requests'

    id = Column(Integer(), primary_key=True, auto_increment=True)
    crawl_id = Column(String(256), nullable=False)
    visit_id = Column(String(256), nullable=False)
    time_stamp = Column(String(256), nullable=False)

    incognito = Column(Integer(), nullable=False)
    extension_session_uuid = Column(String(256), nullable=False)
    event_ordinal = Column(Integer(), nullable=False)
    window_id = Column(Integer(), nullable=False)
    tab_id = Column(Integer(), nullable=False)
    frame_id = Column(Integer(), nullable=False)
    parent_frame_id = Column(Integer(), nullable=False)
    request_id = Column(Integer(), nullable=False)

    url = Column(Text(), nullable=False)
    top_level_url = Column(Text(), nullable=False)
    method = Column(String(256), nullable=False)
    referrer = Column(Text(), nullable=False)
    post_body = Column(Text(), nullable=False)
    post_body_raw = Column(Text(), nullable=False)
    headers = Column(Text(), nullable=False)
    is_XHR = Column(Integer(), nullable=False)
    is_full_page = Column(Integer(), nullable=False)
    is_frame_load = Column(Integer(), nullable=False)
    triggering_origin = Column(Text(), nullable=False)
    loading_origin = Column(Text(), nullable=False)
    loading_href = Column(Text(), nullable=False)
    resource_type = Column(String(256), nullable=False)
    frame_ancestors = Column(Text(), nullable=False)


class DBWebExtHttpResponse(Base):
    __tablename__ = 'http_responses'

    id = Column(Integer(), primary_key=True, auto_increment=True)
    crawl_id = Column(String(256), nullable=False)
    visit_id = Column(String(256), nullable=False)
    time_stamp = Column(String(256), nullable=False)

    incognito = Column(Integer(), nullable=False)
    extension_session_uuid = Column(String(256), nullable=False)
    event_ordinal = Column(Integer(), nullable=False)
    window_id = Column(Integer(), nullable=False)
    tab_id = Column(Integer(), nullable=False)
    frame_id = Column(Integer(), nullable=False)
    request_id = Column(Integer(), nullable=False)

    is_cached = Column(Integer(), nullable=False)
    url = Column(Text(), nullable=False)
    method = Column(String(256), nullable=False)
    response_status = Column(String(256), nullable=False)
    response_status_text = Column(Text(), nullable=False)
    headers = Column(Text(), nullable=False)
    location = Column(Text(), nullable=False)
    content_hash = Column(Text(), nullable=False)


class DBWebExtHttpRedirect(Base):
    __tablename__ = 'http_redirects'

    id = Column(Integer(), primary_key=True, auto_increment=True)
    crawl_id = Column(String(256), nullable=False)
    visit_id = Column(String(256), nullable=False)
    time_stamp = Column(String(256), nullable=False)

    incognito = Column(Integer(), nullable=False)
    extension_session_uuid = Column(String(256), nullable=False)
    event_ordinal = Column(Integer(), nullable=False)
    window_id = Column(Integer(), nullable=False)
    tab_id = Column(Integer(), nullable=False)
    frame_id = Column(Integer(), nullable=False)
    old_request_id = Column(Integer(), nullable=False)
    new_request_id = Column(Integer(), nullable=True)
    old_request_url = Column(Text(), nullable=False)
    new_request_url = Column(Text(), nullable=False)

    response_status = Column(Text(), nullable=False)
    response_status_text = Column(Text(), nullable=False)


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
