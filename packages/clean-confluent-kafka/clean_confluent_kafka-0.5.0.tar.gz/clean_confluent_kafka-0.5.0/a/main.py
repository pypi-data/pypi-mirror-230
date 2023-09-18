from clean_confluent_kafka import KafkaConnection
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

conn = KafkaConnection()

print(conn.export_configs())

message = conn.consume()
print(message)

message = conn.consume()
