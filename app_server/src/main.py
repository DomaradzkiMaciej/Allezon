from db import AerospikeClient
from types import UserTag, UserProfile, Action

from fastapi import FastApi, Response
from datetime import datetime

aerospike_client = AerospikeClient()
app = FastApi()


@app.post("/user_tags")
def user_tags(user_tag):
    date_format = "%Y-%m-%dT%H:%M:%S.%f"
    user_tag.time =  datetime.strptime(user_tag.time, date_format)

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


@app.post("/user_profiles/{cookie}")
def user_profiles(cookie, time_range, debug_response, limit=200):
    user_profile, gen = aerospike_client.get_profile(cookie)
    time_start, time_end = time_range.split('_')

    date_format = "%Y-%m-%dT%H:%M:%S.%f"
    time_start, time_end = datetime.strptime(time_start, date_format), datetime.strptime(time_end, date_format)

    user_profile.buys = list(filter(lambda tag: time_start <= tag.time < time_end, user_profile.buys))
    user_profile.views = list(filter(lambda tag: time_start <= tag.time < time_end, user_profile.views))

    user_profile.buys = user_profile.buys[:-limit]
    user_profile.views = user_profile.views[:-limit]

    if user_profile != debug_response:
        print(f'User profiles difference.\n{user_profile}\n{debug_response}')

    return user_profile


@app.on_event("shutdown")
def shutdown():
    aerospike_client.close()


@app.get("/truncate")
def truncate():
    aerospike_client.truncate()
    return Response(status_code=200)
