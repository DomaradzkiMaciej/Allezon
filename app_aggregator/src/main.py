from db import AerospikeClient
from types_ import UserTag

import kafka
from pydantic import parse_obj_as

import json
import itertools

aerospike_client = AerospikeClient()

kafka_hosts = ['st108vm108.rtb-lab.pl:9092', 'st108vm109.rtb-lab.pl:9092', 'st108vm110.rtb-lab.pl:9092']

admin_client = kafka.KafkaAdminClient(bootstrap_servers=kafka_hosts)
consumer = kafka.KafkaConsumer(bootstrap_servers=kafka_hosts, compression_type='snappy', group_id='aggregation')

try:
    topic_list = [kafka.admin.NewTopic(name='aggregation', num_partitions=2, replication_factor=2)]
    admin_client.create_topics(new_topics=topic_list, validate_only=False)
except kafka.errors.TopicAlreadyExistsError as err:
    pass


def generate_buckets(user_tag: UserTag):
    action = user_tag.action.value
    time = user_tag.time.rsplit(':', 1)[0]

    combinations = itertools.product([user_tag.origin, None], [user_tag.brand_id, None], [user_tag.category_id, None])
    return [f"{action}_{origin}_{brand_id}_{category_id}_{time}" for (origin, brand_id, category_id) in
            combinations]


for msg in consumer:
    user_tag = parse_obj_as(UserTag, json.loads(msg))

    for bucket_name in generate_buckets(user_tag):
        for _ in range(3):
            if aerospike_client.put_aggregated(bucket_name, 1, user_tag.product_info.price):
                break
