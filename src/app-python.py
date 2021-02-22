# https://ddtrace.readthedocs.io/en/stable/integrations.html#flask

import hashlib
import logging
import os
import urllib

import json_log_formatter
import mysql.connector
from flask import Flask, jsonify, make_response, request, send_from_directory

# Sets logs to JSON format when running in a container
if os.environ.get('DD_AGENT_HOST') is not None:
    json_handler = logging.StreamHandler()
    json_handler.setFormatter(json_log_formatter.JSONFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(json_handler)
    root.setLevel(logging.INFO)

logger = logging.getLogger('app-python')

app = Flask(__name__)

@app.route('/health')
def hello():
    return '', 204

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

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
def mysql_test(last_name='Baba'):
    result = ""
    logger.info(f'Retrieving 10 employees with last name {last_name}')
    with mysql.connector.connect(user='admin',
                                 password='senha',
                                 host=os.environ.get(
                                     'APP_MYSQL_HOST', 'mysql'),
                                 port=int(os.environ.get(
                                     'APP_MYSQL_PORT', '3306')),
                                 database='employees') as cnx:
        with cnx.cursor() as cursor:
            query = (
                f'select emp_no, birth_date, first_name, last_name, gender, hire_date from employees where last_name = "{last_name}" limit 10')

            cursor.execute(query)

            for (emp_no, birth_date, first_name, last_name, gender, hire_date) in cursor:
                result += f'{emp_no},{birth_date},{first_name},{last_name},{gender},{hire_date}\n'

    return result, 200, {'Content-Type': 'text/plain'}

@app.route('/error/<int:status>/<msg>')
def return_path(status=200, msg="NONE"):
    span = tracer.current_root_span()
    span.set_tag("error.message", "Error msg")
    span.set_tag("error.stack", "Error stack")
    return msg, status

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
