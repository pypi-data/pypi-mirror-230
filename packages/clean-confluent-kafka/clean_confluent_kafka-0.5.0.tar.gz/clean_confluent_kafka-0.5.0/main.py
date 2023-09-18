import sys
from pathlib import Path

sys.path.append((Path(__file__).parent / "src").as_posix())

from clean_confluent_kafka import KafkaConnection
from clean_confluent_kafka.tools import KafkaConfigsGenerator

# path = Path(__file__).parent / "kafka.yaml"

# conn = KafkaApplication(path)
# print(conn.get_topics_list())
# message = conn.consume()


# print(type(message.value()))

# print(conn.get_topics_list())

# print(KafkaConfigsGenerator("localhost:10808")
#       .add_producer(producer_topic="mytopic")
#       .add_consumer(consumer_topics="myconsumer")
#       .save("ali.yaml"))


#
# app = KafkaApplication()
#
# @app.consume()
# def consume(message):
#       print(message)
#
#
# @app.produce()
# def produce():
#       print(app.broker.get_topics_list())
#       return "hi"
#
#
# if __name__ == "__main__":
#       app()

from clean_confluent_kafka.utils import reverse_flatten_dict, flatten_dict
from pprint import pprint

# config = {'consumer.session.timeout.ms': 250000, 'consumer.message.max.bytes': 10000000, 'consumer.message.copy.max.bytes': 65535, 'consumer.receive.message.max.bytes': 200000000, 'consumer.max.in.flight': 1000000, 'consumer.max.in.flight.requests.per.connection': 1000000, 'consumer.max.poll.interval.ms': 500000, 'consumer.metadata.max.age.ms': 900000, 'consumer.topic.metadata.refresh.sparse': True, 'consumer.topic.metadata.refresh.interval.ms': 50, 'consumer.topic.metadata.refresh.fast.interval.ms': 250, 'consumer.topic.metadata.propagation.max.ms': 30000, 'consumer.broker.address.ttl': 1000, 'consumer.connections.max.idle.ms': 0, 'consumer.reconnect.backoff.ms': 100, 'consumer.reconnect.backoff.max.ms': 10000, 'consumer.statistics.interval.ms': 0, 'consumer.log_level': 6, 'consumer.log.queue': 0, 'consumer.log.thread.name': 1, 'consumer.log.connection.close': True, 'consumer.internal.termination.signal': 0, 'consumer.api.version.request': True, 'consumer.api.version.request.timeout.ms': 1000, 'consumer.api.version.fallback.ms': 0, 'consumer.broker.version.fallback': '0.10.0', 'consumer.security.protocol': 'plaintext', 'consumer.ssl.engine.id': 'dynamic', 'consumer.heartbeat.interval.ms': 80000, 'consumer.auto.offset.reset': 'earliest', 'consumer.enable.auto.commit': True, 'consumer.fetch.max.bytes': 100000000, 'consumer.fetch.message.max.bytes': 50, 'consumer.partition.assignment.strategy': 'range,roundrobin', 'producer.app.max_for_flush': 200, 'producer.message.max.bytes': 50000000, 'producer.batch.size': 5000000, 'producer.linger.ms': 5, 'producer.compression.type': 'snappy', 'producer.acks': 1, 'consumer.app.debug': True, 'consumer.topics': 'da-content-quality', 'consumer.group.id': 'a', 'consumer.bootstrap.servers': '172.17.0.141:9092', 'producer.topic': 'test-produce', 'producer.bootstrap.servers': '172.17.0.141:9092', 'app': None}
config = {'app': None,
          # 'consumer.api.version.fallback.ms': 0,
          # 'consumer.api.version.request': True,
          # 'consumer.api.version.request.timeout.ms': 1000,
          # 'consumer.app.debug': True,
          # 'consumer.auto.offset.reset': 'earliest',
          # 'consumer.bootstrap.servers': '172.17.0.141:9092',
          # 'consumer.broker.address.ttl': 1000,
          # 'consumer.broker.version.fallback': '0.10.0',
          # 'consumer.connections.max.idle.ms': 0,
          # 'consumer.enable.auto.commit': True,
          # 'consumer.fetch.max.bytes': 100000000,
          # 'consumer.fetch.message.max.bytes': 50,
          # 'consumer.group.id': 'a',
          # 'consumer.heartbeat.interval.ms': 80000,
          # 'consumer.internal.termination.signal': 0,
          # 'consumer.log.connection.close': True,
          # 'consumer.log.queue': 0,
          # 'consumer.log.thread.name': 1,
          # 'consumer.log_level': 6,
          'consumer.max.in.flight': 1000000,
          'consumer.max.in.flight.requests.per.connection': 1000000,
          # 'consumer.max.poll.interval.ms': 500000,
          # 'consumer.message.copy.max.bytes': 65535,
          # 'consumer.message.max.bytes': 10000000,
          # 'consumer.metadata.max.age.ms': 900000,
          # 'consumer.partition.assignment.strategy': 'range,roundrobin',
          # 'consumer.receive.message.max.bytes': 200000000,
          # 'consumer.reconnect.backoff.max.ms': 10000,
          # 'consumer.reconnect.backoff.ms': 100,
          # 'consumer.security.protocol': 'plaintext',
          # 'consumer.session.timeout.ms': 250000,
          # 'consumer.ssl.engine.id': 'dynamic',
          # 'consumer.statistics.interval.ms': 0,
          # 'consumer.topic.metadata.propagation.max.ms': 30000,
          # 'consumer.topic.metadata.refresh.fast.interval.ms': 250,
          # 'consumer.topic.metadata.refresh.interval.ms': 50,
          # 'consumer.topic.metadata.refresh.sparse': True,
          # 'consumer.topics': 'da-content-quality',
          # 'producer.acks': 1,
          # 'producer.app.max_for_flush': 200,
          # 'producer.batch.size': 5000000,
          # 'producer.bootstrap.servers': '172.17.0.141:9092',
          # 'producer.compression.type': 'snappy',
          # 'producer.linger.ms': 5,
          # 'producer.message.max.bytes': 50000000,
          'producer.topic': 'test-produce'}


# def reverse_flatten_dict(flattened_dict, sep="."):
#     hierarchical_dict = {}
#     for key, value in flattened_dict.items():
#         keys = key.split(sep)
#         current_dict = hierarchical_dict
#         for k in keys[:-1]:
#             if not isinstance(current_dict, dict):
#                 current_dict = {"self": current_dict}
#             current_dict = current_dict.setdefault(k, {})
#         current_dict[keys[-1]] = value
#     return hierarchical_dict





# def reverse_flatten_dict(flattened_dict, sep="."):
#     hierarchical_dict = {}
#     for key, value in flattened_dict.items():
#         keys = key.split(sep)
#         current_dict = hierarchical_dict
#         for k in keys[:-1]:
#             if k not in current_dict:
#                 current_dict[k] = {}
#             current_dict = current_dict[k]
#         current_key = keys[-1]
#         if 'self' not in current_dict:
#             current_dict[current_key] = {'self': value}
#         else:
#             if not isinstance(current_dict[current_key], dict):
#                 current_dict[current_key] = {'self': current_dict[current_key]}
#             current_dict[current_key]['self'] = value
#     return hierarchical_dict

# Example usage:
# flattened_dict = {'consumer.max.in.flight': 1000000, 'consumer.max.in.flight.requests.per.connection': 1000000}
# hierarchical_dict = reverse_flatten_dict(flattened_dict)
# print(hierarchical_dict)
import os

import json
import yaml

from fastnumbers import try_real

def update_conf_dict_with_env(conf_dict):
    for key in conf_dict:
        # Check if the key is defined in the environment
        key_env = key.replace(".", "_").upper()
        env_var = os.environ.get(key_env, None)
        if env_var is not None:
            conf_dict[key] = yaml.safe_load(env_var)


d = {"key.k1": "1s", "key.k1.k11": 2, "key.k1.k12.k111": 3, "key2": 4}
print(d)
os.environ["KEY_K1"] = "1e8"
update_conf_dict_with_env(d)
print(d)

d2 = {"key": {"k1": {"self": 1, "k11": 2, "k12": {"k111": 3}}}, "key2": 4}

# pprint(d)
# print(flatten_dict(d2))
# import pandas as pd
# df = pd.DataFrame.from_dict(config)
# df.explode()
# print(config == flatten_dict(reverse_flatten_dict(config)))

broker = KafkaConnection(consumer_groups="a")

print("broker")
print(broker.conf.export_config())
# message = broker.consume()
# print(message.value())



# # Example usage:
# d = {"key.k1": 1, "key.k1.k11": 2, "key.k1.k12.k111": 3, "key2": 4}
# print(d == flatten_dict(reverse_flatten_dict(d)))
# print(d2 == reverse_flatten_dict(d))
# print(d2)
