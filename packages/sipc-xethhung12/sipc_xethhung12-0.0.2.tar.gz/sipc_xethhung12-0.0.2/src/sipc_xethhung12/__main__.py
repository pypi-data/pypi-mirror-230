import json
from zoneinfo import ZoneInfo
import datetime as dt

from sipc_xethhung12 import load_config, get_device_name, get_ip, load_kafka, get_ip_event

config = load_config()
deviceName = get_device_name(config)
if __name__ == '__main__':
    tz_hk = ZoneInfo("Asia/Hong_Kong")
    event = get_ip_event(deviceName, tz_hk)
    json_str = json.dumps(event)

    js = json_str.encode('utf-8')
    producer = load_kafka(config)
    rs = producer.send("device-ip-topic", key=deviceName.encode('utf-8'), value=js)
    print(rs.get())
