#!/usr/bin/env python
import json
import re
import uuid

from kafka import KafkaProducer
from urllib.parse import quote

from app import (
    crawl_request_topic,
    CrawlRequest,
)


def publish_message(producer_instance, topic, value):
    try:
        key_bytes = bytes('request', encoding='utf-8')
        value_bytes = bytes(value, encoding='utf-8')
        print(f'Sending Request {value}')
        producer_instance.send(topic, key=key_bytes, value=value_bytes)
        producer_instance.flush()
        print(f'Message published successfully.')
    except Exception as ex:
        print(f'Exception in publishing message.')
        print(ex)


def connect_kafka_producer():
    producer = None
    try:
        producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
    except Exception as ex:
        print('Exception while connecting Kafka')
        print(ex)
    finally:
        return producer


if __name__ == '__main__':
    kafka_producer = connect_kafka_producer()
    topic = crawl_request_topic.get_topic_name()
    if kafka_producer is not None:
        with open('tranco_10k_alexa_10k_union.unlimited_depth_max_10_links.ranked.csv', 'r') as f:
            data = f.read()
        data = data[0:500]  # Just testing for now
        regex = r"(\d+),(.+)"
        matches = re.finditer(regex, data, re.MULTILINE)
        for match in matches:
            grouped = match.groups()
            assert len(grouped) == 2
            id = str(uuid.uuid4())
            url = quote(grouped[1], safe=":/")
            req = CrawlRequest(id=id, url=url).asdict()
            publish_message(kafka_producer, topic, json.dumps(req))
        kafka_producer.close()
