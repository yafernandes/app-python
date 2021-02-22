# https://ddtrace.readthedocs.io/en/stable/integrations.html#flask
from ddtrace import patch

# https://ddtrace.readthedocs.io/en/stable/integrations.html#kombu
patch(kombu=True)

import logging
import os
import time
import socket

import json_log_formatter
from kombu import Connection, Exchange, Queue, Consumer

# Sets logs to JSON format when running in a container
root = logging.getLogger()
if os.environ.get('DD_AGENT_HOST') is not None:
    json_handler = logging.StreamHandler()
    json_handler.setFormatter(json_log_formatter.JSONFormatter())

    root.handlers.clear()
    root.addHandler(json_handler)

logger = logging.getLogger('rabbitmq-consumer')
logger.setLevel(logging.INFO)

RABBITMQ_URL = os.environ.get('APP_RABBITMQ_URL', 'amqp://rabbitmq:5672/')
RABBITMQ_QUEUE = os.environ.get('APP_RABBITMQ_QUEUE', 'datadog')

logger.info(f'Listenning to {RABBITMQ_URL}')

def process_message(body, message):
  time.sleep(.2)
  logger.info(f'Received message [{body}]')
  time.sleep(.2)
  message.ack()

with Connection(RABBITMQ_URL) as conn:
    exchange = Exchange('datadog', type='direct')
    queue = Queue(name=RABBITMQ_QUEUE, exchange=exchange, routing_key='datadog')
    with Consumer(conn, queues=queue, callbacks=[process_message]) as consumer:
        while True:
            try:
                conn.drain_events()
            except socket.timeout:
                conn.heartbeat_check
