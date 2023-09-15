# -*- coding: utf-8 -*-
from patchwork.client.kafka.publisher import AsyncKafkaPublisher
from patchwork.client.kafka.subscriber import AsyncKafkaSubscriber


def test_publisher_dummy():
    producer = AsyncKafkaPublisher(
        kafka_hosts=['localhost']
    )


def test_subscriber_dummy():
    subscriber = AsyncKafkaSubscriber(
        kafka_hosts=['localhost'],
        topics=[],
        consumer_group='test'
    )