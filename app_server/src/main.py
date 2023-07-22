from db import AerospikeClient
from types_ import UserTag, UserProfile, Action

from fastapi import FastAPI, Response
import bisect
from functools import total_ordering
from kafka import KafkaProducer

@total_ordering
class Inversed:
    def __init__(self, x):
        self.x = x

    def __eq__(self, other):
        return self.x == other.x

    def __lt__(self, other):
        return other.x <= self.x


aerospike_client = AerospikeClient()
app = FastAPI()

producer = KafkaProducer(bootstrap_servers=['st108vm101.rtb-lab.pl:9094',
                                            'st108vm102.rtb-lab.pl:9094',
                                            'st108vm103.rtb-lab.pl:9094',
                                            'st108vm104.rtb-lab.pl:9094',
                                            'st108vm105.rtb-lab.pl:9094',
                                            'st108vm106.rtb-lab.pl:9094',
                                            'st108vm107.rtb-lab.pl:9094'])

# {'product_info': {'product_id': 12486, 'brand_id': 'Ebros_Gift', 'category_id': 'Trousers', 'price': 28969}, 'time': '2022-03-01T00:00:00.649Z', 'cookie': '9WkYGxkiXBfpMIjBGURC', 'country': 'CL', 'device': 'MOBILE', 'action': 'VIEW', 'origin': 'CAMPAIGN_321'}
@app.post("/user_tags")
# def user_tags(user_tag: Dict[Any, Any]):
def user_tags(user_tag: UserTag):
    for _ in range(3):
        user_profile, gen = aerospike_client.get_profile(user_tag.cookie)
        action_list = user_profile.buys if user_tag.action == Action.BUY else user_profile.views

        idx = next((i for i, tag in enumerate(action_list) if user_tag.time >= tag.time ), len(action_list))
        action_list.insert(idx, user_tag)

        # bisect.insort(action_list, user_tag, key=lambda tag: Inversed(tag.time))

        del action_list[200:]

        if aerospike_client.put_profile(user_profile, gen):
            producer.send('aggregation', user_profile.model_dump())
            return Response(status_code=204)
        else:
            continue

    return Response(status_code=400)


# /user_profiles/yJKX3u9HOTlcaDipwAmb?time_range=2022-03-01T00:00:01.610_2022-03-01T00:00:02.419&limit=200
@app.post("/user_profiles/{cookie}")
def user_profiles(cookie: str, time_range: str, debug_response: UserProfile, limit: int = 200):
    user_profile, gen = aerospike_client.get_profile(cookie)
    time_start, time_end = time_range.split('_')

    user_profile.buys = list(filter(lambda tag: time_start <= tag.time < time_end, user_profile.buys))
    user_profile.views = list(filter(lambda tag: time_start <= tag.time < time_end, user_profile.views))

    user_profile.buys = user_profile.buys[:limit]
    user_profile.views = user_profile.views[:limit]

    # if user_profile != debug_response:
    #     print(f'User profiles difference.\n{user_profile}\n{debug_response}')

    return user_profile


@app.on_event("shutdown")
def shutdown():
    aerospike_client.close()


@app.get("/truncate")
def truncate():
    aerospike_client.truncate()
    return Response(status_code=200)


@app.get("/hostname")
def hostname():
    hostname = open('/etc/hostname').read()
    return {'hostname': hostname}
