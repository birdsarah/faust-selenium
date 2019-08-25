from datetime import datetime  # noqa

from sqlalchemy import Column, Integer, Text, String, Boolean, ForeignKey, DateTime  # noqa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Session = sessionmaker()
Base = declarative_base()


class DBCrawlRequest(Base):
    __tablename__ = 'crawl_requests'

    id = Column(String(256), primary_key=True)
    url = Column(Text(), nullable=False)


class DBCrawlResult(Base):
    __tablename__ = 'crawl_results'

    id = Column(String(256), primary_key=True)
    request_id = Column(String(256), nullable=False)
    url = Column(Text(), nullable=False)
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
