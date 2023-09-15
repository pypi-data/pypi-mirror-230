import argparse
import json
from zoneinfo import ZoneInfo

from sipc_xethhung12 import load_config, get_device_name, get_ip_event
from sipc_xethhung12.cmd import gen
from sipc_xethhung12.cmd.subscribeCmd import load_data
from sipc_xethhung12.utils.kafka import get_producer

tz_hk = ZoneInfo("Asia/Hong_Kong")


def publish(device_name, public_config):
    event = get_ip_event(device_name, tz_hk, public_config)
    json_str = json.dumps(event)
    js = json_str.encode('utf-8')
    producer = get_producer(public_config)
    rs = producer.send("device-ip-topic", key=device_name.encode('utf-8'), value=js)
    return rs.get()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='SCIP',
        description='A program manage distributed device ip through event driven architecture',
        epilog='Text at the bottom of help')
    parser.add_argument('-p', '--publish', action='store_true', help='Publish event to Kafka')
    parser.add_argument('-s', '--subscribe', action='store_true', help='Subscribe event from Kafka')
    parser.add_argument('-c', '--cast', action='store_true', help='List all devices')
    parser.add_argument('--config', help='Config file path', default="config.yaml")
    parser.add_argument('--from-start', action='store_true', help='Start from beginning [subscribe mode only]')
    parser.add_argument('--server-env', action='store_true', help='Server environment file generation [cast mode only]')
    parser.add_argument('-o', '--output-file', help='Output file [subscribe mode only]', default='devices.yaml')
    parser.add_argument('-i', '--input-file', help='Input file [cast mode only]', default='devices.yaml')
    parser.add_argument('--output-dir', help='Output file directory [cast mode only]', default=".")

    args = parser.parse_args()

    test_multiple_select = sum(map(lambda x: 1 if x else 0, [args.publish, args.subscribe, args.cast]))

    if test_multiple_select < 1:
        raise Exception("No action selected")
    if test_multiple_select > 1:
        raise Exception("Multiple action selected")

    if args.config is None or args.config == "":
        raise Exception("Config file path is empty")

    config = load_config(args.config)
    if args.publish:
        deviceName = get_device_name(config)
        print(publish(deviceName, config))
    elif args.subscribe:
        load_data(config, tz_hk, args.output_file, args.from_start)
    elif args.cast:
        gen(args.input_file, args.output_dir)
    else:
        raise Exception("Unknown error")
