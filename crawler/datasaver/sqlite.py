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
    # The fields here should match the
    # KafkaLogHandler in app.py
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


class DBJavascript(Base):
    __tablename__ = 'javascript'

    id = Column(Integer(), primary_key=True, auto_increment=True)

    top_level_url = Column(Text())
    document_url = Column(Text())
    script_url = Column(Text())

    crawl_id = Column(Integer())
    visit_id = Column(Integer())

    extension_session_uuid = Column(String(256))
    event_ordinal = Column(Integer())
    page_scoped_event_orginal = Column(Integer())
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
    value = Column(Text())  # Max length?
    time_stamp = Column(String(256))  # Parse?
    incognito = Column(Integer())


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
