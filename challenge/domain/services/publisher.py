import json
from traceback import print_exc

import pika
from dynaconf import settings

from challenge.domain.services.errors import PublisherError
from challenge.utils.logging import logger


class Publisher(object):
    def __init__(self, queue, url=settings.RABBITMQ_URL):
        self._url = url
        self._queue = queue

        try:
            logger.info('connecting to RabbitMQ...')
            self._connection = pika.BlockingConnection(pika.URLParameters(url))

            logger.info('opening a RabbitMQ channel...')
            self._channel = self._connection.channel()

            self._channel.exchange_declare('unbabel', exchange_type='topic')

            logger.info(f'declaring RabbitMQ queue {self._queue}...')
            self._channel.queue_declare(self._queue, durable=True)

            logger.info(f'binding RabbitMQ exchange to queue {self._queue}...')
            self._channel.queue_bind(self._queue, 'unbabel')
        except Exception:
            print_exc()
            raise PublisherError(
                f'Failed to start a connection with RabbitMQ.')

    def publish(self, message):
        if self._channel is None or not self._channel.is_open:
            logger.error('no RabbitMQ channel open')
            raise PublisherError(
                f'Failed to start a connection with RabbitMQ: '
                f'no RabbitMQ channel open.')

        properties = pika.BasicProperties(
            content_type='text/json', delivery_mode=1)

        self._channel.basic_publish('unbabel', self._queue,
                                    json.dumps(message), properties)

        logger.debug('published message')
