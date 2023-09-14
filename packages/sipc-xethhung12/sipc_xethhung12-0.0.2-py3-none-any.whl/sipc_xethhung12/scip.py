import datetime as dt
import json
import os.path
import traceback

import requests
import yaml
from kafka import KafkaProducer


def load_config():
    config_path = "config.yaml"
    if not os.path.exists(config_path):
        raise Exception("Configuration not found")

    with open(config_path) as f:
        text = f.read()

        return yaml.safe_load(text)


def load_kafka(config):
    kafkaConfig = config['kafka-config']
    if kafkaConfig['type'] == 1:
        kafkaConfig = kafkaConfig['value']

        producer = KafkaProducer(
            bootstrap_servers=kafkaConfig['bootstrap_servers'],
            sasl_mechanism=kafkaConfig['sasl_mechanism'],
            security_protocol=kafkaConfig['security_protocol'],
            sasl_plain_username=kafkaConfig['sasl_plain_username'],
            sasl_plain_password=kafkaConfig['sasl_plain_password'],
        )
        return producer
    else:
        raise Exception("No supported kafka config")


def get_ip():
    try:
        m = json.loads(requests.get("https://api.myip.com").text)
        return m['ip']
    except Exception as ex:
        traceback.print_exc()
        raise Exception("Fail to get ip address")


def get_device_name(config):
    return config['device-name']


def get_ip_event(deviceName, tz):
    ip = get_ip()
    time_string = dt.datetime.now().astimezone(tz=tz).isoformat()
    return {'server': deviceName, 'ip': ip, 'time': time_string}
