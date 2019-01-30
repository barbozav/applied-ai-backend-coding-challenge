from dynaconf import settings
import pika
import json

from challenge.utils.logging import logger


class Publisher(object):
    def __init__(self, queue, url=settings.RABBITMQ_URL):
        self._url = url
        self._queue = queue

        logger.info('connecting to RabbitMQ...')
        self._connection = pika.BlockingConnection(pika.URLParameters(url))

        logger.info('opening a RabbitMQ channel...')
        self._channel = self._connection.channel()

        self._channel.exchange_declare('unbabel', exchange_type='topic')

        logger.info(f'declaring RabbitMQ queue {self._queue}...')
        self._channel.queue_declare(self._queue, durable=True)

        logger.info(f'binding RabbitMQ exchange to queue {self._queue}...')
        self._channel.queue_bind(self._queue, 'unbabel')

    def publish(self, message):
        if self._channel is None or not self._channel.is_open:
            logger.error('no RabbitMQ channel open')
            return

        properties = pika.BasicProperties(
            content_type='text/json', delivery_mode=1)

        self._channel.basic_publish('unbabel', self._queue,
                                    json.dumps(message), properties)

        logger.debug('published message')
