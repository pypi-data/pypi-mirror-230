import datetime as dt
import json
import os.path
import traceback

import requests
import yaml


def load_config(config_path):
    if not os.path.exists(config_path):
        raise Exception("Configuration not found")

    with open(config_path) as f:
        text = f.read()

        return yaml.safe_load(text)




def get_ip():
    try:
        m = json.loads(requests.get("https://api.myip.com").text)
        return m['ip']
    except Exception as ex:
        traceback.print_exc()
        raise Exception("Fail to get ip address")


def get_device_name(config):
    return config['device-name']


def get_ip_event(deviceName, tz, config):
    ip = get_ip()
    time_string = dt.datetime.now().astimezone(tz=tz).isoformat()

    pair_str = 'attached-pair'
    if pair_str in config:
        attached_pair = config[pair_str]
    else:
        attached_pair = {}
    return {'server': deviceName, 'ip': ip, 'time': time_string, 'extra': attached_pair}
