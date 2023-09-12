import json
from contextlib import contextmanager
from dataclasses import dataclass

import pika
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection

from .config import CONFIG


@dataclass
class Publisher:
    """
    Pre-configured publisher

    ```
    @contextmanager
    def student_notice() -> Publisher:
        with rabbitmq_channel() as channel:
            yield Publisher(channel=channel, exchange="etna", routing_key="student_notice")


    with student_notice() as notice:
        notice.publish(my_bytes)
    ```
    """

    channel: BlockingChannel
    exchange: str
    routing_key: str

    def publish(self, body: bytes, properties=None, mandatory: bool = False):
        self.channel.basic_publish(self.exchange, self.routing_key, body, properties=properties, mandatory=mandatory)


class JSONPublisher(Publisher):
    """
    Pre-configured JSON publisher

    ```
    @contextmanager
    def student_notice() -> Publisher:
        with rabbitmq_channel() as channel:
            yield JSONPublisher(channel=channel, exchange="etna", routing_key="student_notice")


    with student_notice() as notice:
        notice.publish(my_data)
    ```
    """

    def publish(self, body, properties=None, mandatory: bool = False):
        encoded_json_body = json.dumps(body).encode()
        return super().publish(encoded_json_body, properties=properties, mandatory=mandatory)


@contextmanager
def rabbitmq_connection() -> BlockingConnection:
    params = pika.URLParameters(CONFIG.rabbitmq.url)
    with pika.BlockingConnection(params) as connection:
        yield connection


@contextmanager
def rabbitmq_channel() -> BlockingChannel:
    with rabbitmq_connection() as connection:
        with connection.channel() as channel:
            yield channel
