from db import AerospikeClient
from types_ import UserTag

import kafka
from pydantic import TypeAdapter

import itertools

aerospike_client = AerospikeClient()

kafka_hosts = ['st108vm109.rtb-lab.pl:9092',
               'st108vm110.rtb-lab.pl:9092']

admin_client = kafka.KafkaAdminClient(bootstrap_servers=kafka_hosts)

try:
    topic_list = [kafka.admin.NewTopic(name='aggregation', num_partitions=6, replication_factor=2,
                                       topic_configs={'retention.ms': 86400000})]
    admin_client.create_topics(new_topics=topic_list, validate_only=False)
except kafka.errors.TopicAlreadyExistsError as err:
    pass

consumer = kafka.KafkaConsumer('aggregation', bootstrap_servers=kafka_hosts, group_id='aggregation')


def generate_buckets_names(user_tag: UserTag):
    action = user_tag.action.value
    time = user_tag.time.rsplit(':', 1)[0] + ':00'

    bucket_data = itertools.product([user_tag.origin, None], [user_tag.product_info.brand_id, None],
                                     [user_tag.product_info.category_id, None])
    return [f"{action}_{origin}_{brand_id}_{category_id}_{time}" for (origin, brand_id, category_id) in
            bucket_data]


type_adapter = TypeAdapter(UserTag)

for msg in consumer:
    user_tag = type_adapter.validate_json(msg.value)

    for bucket_name in generate_buckets_names(user_tag):
        for _ in range(3):
            if aerospike_client.put_aggregated(bucket_name, 1, user_tag.product_info.price):
                break
