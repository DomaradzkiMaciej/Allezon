from typing import Any, Dict
from db import AerospikeClient
from types_ import UserTag, UserProfile, Action

from fastapi import FastAPI, Response
from datetime import datetime



aerospike_client = AerospikeClient()
app = FastAPI()

# {'product_info': {'product_id': 12486, 'brand_id': 'Ebros_Gift', 'category_id': 'Trousers', 'price': 28969}, 'time': '2022-03-01T00:00:00.649Z', 'cookie': '9WkYGxkiXBfpMIjBGURC', 'country': 'CL', 'device': 'MOBILE', 'action': 'VIEW', 'origin': 'CAMPAIGN_321'}
@app.post("/user_tags")
# def user_tags(user_tag: Dict[Any, Any]):
def user_tags(user_tag: UserTag):
    # print(user_tag)
    # ut = UserTag.parse_obj(user_tag)
    # print(ut)
    # date_format = "%Y-%m-%dT%H:%M:%S.%f"
    # user_tag.time = datetime.strptime(user_tag.time, date_format)

    for _ in range(3):
        user_profile, gen = aerospike_client.get_profile(user_tag.cookie)
        action_list = user_profile.buys if user_tag.action == Action.BUY else user_profile.views
        action_list.append(user_tag)
        action_list.sort(key=lambda t: t.time, reverse=True)
        del action_list[200:]

        if aerospike_client.put_profile(user_profile, gen):
            return Response(status_code=204)
        else:
            continue

    return Response(status_code=400)

# /user_profiles/yJKX3u9HOTlcaDipwAmb?time_range=2022-03-01T00:00:01.610_2022-03-01T00:00:02.419&limit=200
@app.post("/user_profiles/{cookie}")
def user_profiles(cookie: str, time_range: str, debug_response: UserProfile, limit: int = 200):
    user_profile, gen = aerospike_client.get_profile(cookie)
    time_start, time_end = time_range.split('_')

    # date_format = "%Y-%m-%dT%H:%M:%S.%f"
    # time_start, time_end = datetime.strptime(time_start, date_format), datetime.strptime(time_end, date_format)

    # print(user_profile)

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
