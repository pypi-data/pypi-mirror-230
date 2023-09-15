import datetime as dt
import json
import os

import yaml
from kafka import TopicPartition, OffsetAndMetadata

from sipc_xethhung12.utils.kafka import get_consumer


def load_devices(device_path):
    if not os.path.exists(device_path):
        save_devices({}, device_path)
    with open(device_path, "r") as f:
        s = f.read()
        return yaml.safe_load(s)


def save_devices(devices, device_path):
    s = yaml.safe_dump(devices)
    with open(device_path, 'w') as f:
        f.write(s)


def loading_framework(consumer, device_path, max_count=50):
    count = -1
    data = {}
    while True:
        msg = consumer.poll(100)
        if len(msg) == 0:
            if count > max_count:
                print("Shutting down due to no more event")
                break
            if count == -1:
                count = 0
            else:
                count += 1
        else:
            count = -1
            _, event = msg.popitem()
            max_offset_pair = {}
            for e in event:
                newTopicPartition = TopicPartition(e.topic, e.partition)
                newOffset = e.offset
                if newTopicPartition not in max_offset_pair:
                    max_offset_pair[newTopicPartition] = OffsetAndMetadata(newOffset + 1, None)
                else:
                    if max_offset_pair[newTopicPartition].offset < newOffset + 1:
                        max_offset_pair[newTopicPartition] = OffsetAndMetadata(newOffset + 1, None)

                k = e.key.decode('utf-8')
                v = e.value.decode('utf-8')
                print(k)
                print(v)
                data[k] = v

            devices = load_devices(device_path)
            for k in data:
                devices[k] = json.loads(data[k])
            save_devices(devices, device_path)
            print("Data to process: ")
            print(data)
            consumer.commit(max_offset_pair)


def load_data(config, timezone, output_path, from_start: bool = False):
    print("First start")
    print(dt.datetime.now(tz=timezone).isoformat())
    consumer = get_consumer(config)
    if from_start:
        consumer.poll(100)
        assigned = consumer.assignment()
        for a in assigned:
            consumer.seek_to_beginning(a)
    loading_framework(consumer,output_path)

# if __name__ == '__main__':
#     print("First start")
#     print(dt.datetime.now(tz=ZoneInfo("Asia/Hong_Kong")).isoformat())
#     # consumer = get_consumer()
#     # consumer.poll(30)
#     # assigned = consumer.assignment()
#     # for a in assigned:
#     #     consumer.seek_to_beginning(a)
#     # while True:
#     consumer = get_consumer()
#     consumer.poll(30)
#     print(dt.datetime.now(tz=ZoneInfo("Asia/Hong_Kong")).isoformat())
#
#     count = -1
#     data = {}
#     while True:
#         msg = consumer.poll(100)
#         if len(msg) == 0:
#             if count > 100:
#                 print("Too many empty")
#                 break
#             if count == -1:
#                 count = 0
#             else:
#                 count += 1
#         else:
#             count = -1
#             _, event = msg.popitem()
#             max_offset_pair = {}
#             for e in event:
#                 newTopicPartition = TopicPartition(e.topic, e.partition)
#                 newOffset = e.offset
#                 if newTopicPartition not in max_offset_pair:
#                     max_offset_pair[newTopicPartition] = OffsetAndMetadata(newOffset + 1, None)
#                 else:
#                     if max_offset_pair[newTopicPartition].offset < newOffset + 1:
#                         max_offset_pair[newTopicPartition] = OffsetAndMetadata(newOffset + 1, None)
#
#                 k = e.key.decode('utf-8')
#                 v = e.value.decode('utf-8')
#                 print(k)
#                 print(v)
#                 data[k] = v
#
#             print("Data to process: ")
#             devices = load_device()
#             for k in data:
#                 devices[k] = json.loads(data[k])
#             save_device(devices)
#             print(data)
#             consumer.commit(max_offset_pair)
#
#     # print(datetime.datetime.now(tz=ZoneInfo("Asia/Hong_Kong")).isoformat())
#     # consumer.close()
#     # print("Sleep for 1 hour")
#     # time.sleep(60)
