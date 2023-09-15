from kafka import KafkaProducer, KafkaConsumer


def get_consumer(config):
    kafkaConfig = config['kafka-config']
    if kafkaConfig['type'] != 1:
        raise Exception("No supported kafka config")
    kafkaConfig = kafkaConfig['value']
    return KafkaConsumer(
        kafkaConfig['consumer']['topic'],
        bootstrap_servers=kafkaConfig['bootstrap_servers'],
        sasl_mechanism=kafkaConfig['sasl_mechanism'],
        security_protocol=kafkaConfig['security_protocol'],
        sasl_plain_username=kafkaConfig['sasl_plain_username'],
        sasl_plain_password=kafkaConfig['sasl_plain_password'],
        group_id=kafkaConfig['consumer']['group_id'],
        enable_auto_commit=False,
        auto_offset_reset='earliest',
    )

def get_producer(config):
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
