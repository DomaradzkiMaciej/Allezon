from db import AerospikeClient
from types_ import UserTag, UserProfile, Action, Aggregated, Aggregate

from fastapi import FastAPI, Response, Query
import kafka

import bisect
from functools import total_ordering
import datetime
from typing import List


@total_ordering
class Inversed:
    def __init__(self, x):
        self.x = x

    def __eq__(self, other):
        return self.x == other.x

    def __lt__(self, other):
        return other.x <= self.x


def normalize_time(datatime: str):
    if '.' in datatime:
        return datatime[:-1]
    else:
        return datatime[:-1] + '.000'


aerospike_client = AerospikeClient()
app = FastAPI()

kafka_hosts = ['st108vm109.rtb-lab.pl:9092',
               'st108vm110.rtb-lab.pl:9092']

admin_client = kafka.KafkaAdminClient(bootstrap_servers=kafka_hosts)
producer = kafka.KafkaProducer(bootstrap_servers=kafka_hosts, compression_type="snappy")

try:
    topic_list = [kafka.admin.NewTopic(name='aggregation', num_partitions=6, replication_factor=2,
                                       topic_configs={'retention.ms': 86400000})]
    admin_client.create_topics(new_topics=topic_list, validate_only=False)
except kafka.errors.TopicAlreadyExistsError as err:
    pass


# {'product_info': {'product_id': 12486, 'brand_id': 'Ebros_Gift', 'category_id': 'Trousers', 'price': 28969}, 'time': '2022-03-01T00:00:00.649Z', 'cookie': '9WkYGxkiXBfpMIjBGURC', 'country': 'CL', 'device': 'MOBILE', 'action': 'VIEW', 'origin': 'CAMPAIGN_321'}
@app.post("/user_tags")
# def user_tags(user_tag: Dict[Any, Any]):
def user_tags(user_tag: UserTag):
    for _ in range(3):
        user_profile, gen = aerospike_client.get_profile(user_tag.cookie)
        action_list = user_profile.buys if user_tag.action == Action.BUY else user_profile.views
        bisect.insort(action_list, user_tag, key=lambda tag: Inversed(tag.time[:-1]))
        del action_list[200:]

        if aerospike_client.put_profile(user_profile, gen):
            producer.send('aggregation', user_tag.model_dump_json().encode('utf-8'))
            return Response(status_code=204)
        else:
            continue

    return Response(status_code=400)


# /user_profiles/yJKX3u9HOTlcaDipwAmb?time_range=2022-03-01T00:00:01.610_2022-03-01T00:00:02.419&limit=200
@app.post("/user_profiles/{cookie}")
def user_profiles(cookie: str, time_range: str, debug_response: UserProfile, limit: int = 200):
    user_profile, gen = aerospike_client.get_profile(cookie)
    time_start, time_end = time_range.split('_')

    user_profile.buys = list(filter(lambda tag: time_start <= normalize_time(tag.time) < time_end, user_profile.buys))
    user_profile.views = list(filter(lambda tag: time_start <= normalize_time(tag.time) < time_end, user_profile.views))

    user_profile.buys = user_profile.buys[:limit]
    user_profile.views = user_profile.views[:limit]

    # if user_profile.buys != debug_response.buys:
    #     print(f'User profiles buys difference. time_start={time_start}, time_end={time_end}, limit={limit}')
    #     print([tag.time for tag in user_profile.buys])
    #     print([tag.time for tag in debug_response.buys])
    # elif user_profile.views != debug_response.views:
    #     print(f'User profiles views difference. time_start={time_start}, time_end={time_end}, limit={limit}')
    #     print([tag.time for tag in user_profile.views])
    #     print([tag.time for tag in debug_response.views])

    return user_profile


# /aggregates?time_range=2022-03-01T00:01:00_2022-03-01T00:02:00&action=VIEW&category_id=Shoes___Accessories&aggregates=COUNT&aggregates=SUM_PRICE
@app.post("/aggregates")
def aggregates(time_range: str, action: Action, debug_response: Aggregated, aggregates: List[Aggregate] = Query(...),
               origin: str = None, brand_id: str = None, category_id: str = None):
    buckets_starts = generate_bucket_starts(time_range)
    bucket_name = f"{action}_{origin}_{brand_id}_{category_id}_"
    buckets_names = [bucket_name + bucket_start for bucket_start in buckets_starts]
    buckets = aerospike_client.get_aggregates(buckets_names)

    response = Aggregated.model_validate({'columns': ["1m_bucket", "action"], 'rows': []})
    row_base = [action.value]

    if origin is not None:
        response.columns.append("origin")
        row_base.append(origin)

    if brand_id is not None:
        response.columns.append("brand_id")
        row_base.append(brand_id)

    if category_id is not None:
        response.columns.append("category_id")
        row_base.append(category_id)

    response.columns.extend([aggregate.value.lower() for aggregate in aggregates])
    response.rows = [[buckets_start] + row_base for buckets_start in buckets_starts]

    for (i, bucket) in enumerate(buckets):
        for aggregate in aggregates:
            if bucket is not None:
                response.rows[i].append(str(bucket[aggregate.value]))
            else:
                response.rows[i].append('0')

    # if response != debug_response:
    #     print('Aggregates difference')
    #     print(response)
    #     print(debug_response)

    return response


def generate_bucket_starts(time_range: str):
    time_start, time_end = time_range.split('_')
    datetime_format = "%Y-%m-%dT%H:%M:%S"
    time_start = datetime.datetime.strptime(time_start, datetime_format)
    time_end = datetime.datetime.strptime(time_end, datetime_format)

    bucket_starts = []
    while time_start < time_end:
        bucket_starts.append(time_start.strftime(datetime_format))
        time_start += datetime.timedelta(minutes=1)

    return bucket_starts


@app.on_event("shutdown")
def shutdown():
    aerospike_client.close()


@app.get("/truncate")
def truncate():
    aerospike_client.truncate()
    return Response(status_code=200)


@app.get("/hostname")
def hostname():
    hostname_ = open('/etc/hostname').read()
    return {'hostname': hostname_}
