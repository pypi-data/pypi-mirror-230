import logging

import jsonpickle
import pika
from detecta_shared.abstractions.integration_events import IntegrationEvent

from detecta_shared.rabbitmq.rabbitmq_connection import RabbitMQConnection

from detecta_shared.rabbitmq.rabbitmq_params import RabbitMQPublisherParams, RabbitMQSendParams


class RabbitMQPublisher:

    def __init__(self, params: RabbitMQPublisherParams, connection: RabbitMQConnection, logger: logging.Logger):
        self._logger = logger
        self._connection = connection
        self._publisher_params = params
        self._channel = None

    def _publish(self, event: IntegrationEvent, message_params: RabbitMQSendParams):
        if not self._connection.is_connected():
            self._connection.try_connect()
        channel = self._connection.create_channel()
        self._logger.info(f"Channel RabbitMQ created to send: {type(event).__name__}")
        with channel:
            body = jsonpickle.dumps(event, unpicklable=False).encode()
            live_time = None
            if message_params.message_live_milliseconds:
                live_time = str(message_params.message_live_milliseconds)
            self._logger.info(f"Publishing to RabbitMQ {type(event).__name__} ")
            channel.basic_publish(exchange=self._publisher_params.exchange,
                                  routing_key=message_params.routing_key,
                                  body=body, properties=pika.BasicProperties(delivery_mode=2,
                                                                             expiration=live_time))

    def publish(self, event: IntegrationEvent, message_params: RabbitMQSendParams):
        try:
            self._publish(event, message_params)
        except (pika.exceptions.ConnectionClosed, pika.exceptions.ChannelWrongStateError):
            self._logger.warning("Connection closed, reconnecting to rabbitmq")
            self._connection.try_connect()
            self._publish(event, message_params)
