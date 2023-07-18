from types_ import UserTag, UserProfile, Action
import jsonpickle
import aerospike
from pydantic import parse_obj_as
import json

class AerospikeClient():
    namespace = 'allezon'
    set = 'user_tags'

    config = {
        'hosts': [
            # ('st111vm105.rtb-lab.pl', 3000),
            # ('st111vm106.rtb-lab.pl', 3000),
            ('st111vm107.rtb-lab.pl', 3000),
            ('st111vm108.rtb-lab.pl', 3000),
            ('st111vm109.rtb-lab.pl', 3000),
            ('st111vm110.rtb-lab.pl', 3000)

        ],
        'policies': {
            'timeout': 10000  # milliseconds
        }
    }

    def __init__(self):
        self.client = aerospike.client(self.config)
        self.client.connect()

    def close(self):
        self.client.close()

    def truncate(self):
        self.client.truncate(self.namespace, self.set, 0)

    def get_profile(self, cookie):
        try:
            if not self.client.is_connected():
                self.client.connect()

            key = (self.namespace, self.set, cookie)
            key, meta, bins = self.client.get(key)
            # buys = jsonpickle.decode(bins['buys'])
            # views = jsonpickle.decode(bins['views'])
            buys = parse_obj_as(list[UserTag], json.loads(bins['buys']))
            views = parse_obj_as(list[UserTag], json.loads(bins['views']))
            

            return UserProfile.parse_obj({"cookie": cookie, "buys": buys, "views": views}), meta['gen']

        except aerospike.exception.RecordNotFound:
            return UserProfile.parse_obj({"cookie": cookie, "buys": [], "views": []}), 0

    def put_profile(self, user_profile, gen):
        try:
            if not self.client.is_connected():
                self.client.connect()

            key = (self.namespace, self.set, user_profile.cookie)

            # buys = jsonpickle.encode(user_profile.buys)
            # views = jsonpickle.encode(user_profile.views)

            # print([v.model_dump() for v in user_profile.views])
            # print([b.model_dump() for b in user_profile.buys])
            buys = json.dumps([b.model_dump() for b in user_profile.buys], default=str)
            views = json.dumps([v.model_dump() for v in user_profile.views], default=str)

            meta = {'gen': gen}
            policy = ({'gen': aerospike.POLICY_GEN_EQ})
            bins = {'cookie': user_profile.cookie, 'buys': buys, 'views': views}

            # print(f'Writing to Aerospike. User cookie: {UserProfile.cookie}, bins: {bins}')

            self.client.put(key, bins, meta=meta, policy=policy)
            return True

        except aerospike.exception.RecordGenerationError:
            return False

        except aerospike.exception.AerospikeError as e:
            print(f'Error {e} while trying to write to Aerospike. User cookie: {UserProfile.cookie}')
            return False