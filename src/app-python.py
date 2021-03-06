# https://ddtrace.readthedocs.io/en/stable/integrations.html#flask
import hashlib
import logging
import os
import random
import sys
import urllib

import json_log_formatter
import mysql.connector
from ddtrace import patch, tracer
from flask import Flask, jsonify, make_response, request, send_from_directory, render_template
from kombu import Connection

# https://ddtrace.readthedocs.io/en/stable/integrations.html#kombu
patch(kombu=True)


# Sets logs to JSON format when running in a container
root = logging.getLogger()
if os.environ.get('DD_AGENT_HOST') is not None:
    json_handler = logging.StreamHandler(sys.stdout)
    json_handler.setFormatter(json_log_formatter.JSONFormatter())

    root.handlers.clear()
    root.addHandler(json_handler)

logger = logging.getLogger('app-python')
logger.setLevel(logging.INFO)

app = Flask(__name__)

random.seed()

MYSQL_HOST = os.environ.get('APP_MYSQL_HOST', 'mysql')
MYSQL_PORT = int(os.environ.get('APP_MYSQL_PORT', '3306'))
RABBITMQ_URL = os.environ.get('APP_RABBITMQ_URL', 'amqp://rabbitmq:5672/')
DD_VERSION = os.environ.get('DD_VERSION', '0.1')
DD_CLIENT_TOKEN = os.environ.get('DD_CLIENT_TOKEN')
DD_APPLICATION_ID = os.environ.get('DD_APPLICATION_ID')
DD_SITE = os.environ.get('DD_SITE', 'datadoghq.com')


@app.route('/health')
def hello():
    return '', 204


@app.route('/lab')
def lab_page():
    return render_template('lab.html', clientToken=DD_CLIENT_TOKEN, applicationId=DD_APPLICATION_ID, site=DD_SITE)


@app.route('/sha512')
def sha512():
    logger.info(f'Calculating SHA512 for {request.args.get("url")}')
    hash = hashlib.sha512()
    with urllib.request.urlopen(request.args.get('url')) as response:
        while True:
            data = response.read(4096)
            if not data:
                break
            hash.update(data)
    return hash.hexdigest(), 200


@app.route('/mysql/employee/<last_name>')
def mysql_employee(last_name='Baba'):
    result = ""
    logger.info(f'Retrieving 10 employees with last name {last_name}')
    with mysql.connector.connect(user='admin',
                                 password='senha',
                                 host=MYSQL_HOST,
                                 port=MYSQL_PORT,
                                 database='employees') as cnx:
        with cnx.cursor() as cursor:
            query = (
                f'select emp_no, birth_date, first_name, last_name, gender, hire_date from employees where last_name = "{last_name}" limit 10')

            cursor.execute(query)

            for (emp_no, birth_date, first_name, last_name, gender, hire_date) in cursor:
                result += f'{emp_no},{birth_date},{first_name},{last_name},{gender},{hire_date}\n'

    return result, 200, {'Content-Type': 'text/plain'}


@app.route('/rabbitmq/send/<queue>', methods=['POST', 'GET'])
def rabbitmq_send(queue='datadog'):
    message = request.data.decode(
        'UTF-8') if request.method == 'POST' else 'Hello there!'
    logger.info(f'Sending message to RabbitMQ [{message}]')
    with Connection(RABBITMQ_URL) as conn:
        with conn.SimpleQueue(queue) as queue:
            queue.put(message)
    return "Success", 200, {'Content-Type': 'text/plain'}


@app.route('/error/<int:status>/<msg>')
def return_path(status=200, msg="NONE"):
    span = tracer.current_root_span()
    span.set_tag("error.message", "Error msg")
    span.set_tag("error.stack", "Error stack")
    return msg, status


@app.route('/api/random')
def api_random():
    if DD_VERSION == '0.2':
        return "Success", 200
    else:
        if random.randint(1, 100) > 20:
            logger.error('The hyperdriver did not repond in time.')
            tracer.current_root_span().set_tag("error.message", "Hyperdriver not active")
            tracer.current_root_span().set_tag("error.type", "Time travel")
            return "Not today", 500
        else:
            return "Success", 200
    logger.info("point5")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
