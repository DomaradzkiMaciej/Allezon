from types_ import UserTag, UserProfile
import aerospike
from pydantic import TypeAdapter
import json
import snappy


class AerospikeClient:
    namespace = 'allezon'
    set = 'user_tags'
    set_aggregated = 'aggregated'

    config = {
        'hosts': [
            ('st108vm106.rtb-lab.pl', 3000),
            ('st108vm107.rtb-lab.pl', 3000),
            ('st108vm108.rtb-lab.pl', 3000),
            ('st108vm109.rtb-lab.pl', 3000),
            ('st108vm110.rtb-lab.pl', 3000)

        ],
        'policies': {
            'timeout': 10000  # milliseconds
        }
    }

    def __init__(self):
        self.client = aerospike.client(self.config)
        self.client.connect()
        self.type_adapter = TypeAdapter(list[UserTag])

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
            buys = self.type_adapter.validate_json(snappy.decompress(bins['buys']))
            views = self.type_adapter.validate_json(snappy.decompress(bins['views']))

            return UserProfile.model_validate({"cookie": cookie, "buys": buys, "views": views}), meta['gen']

        except aerospike.exception.RecordNotFound:
            return UserProfile.model_validate({"cookie": cookie, "buys": [], "views": []}), 0

    def get_aggregates(self, bucket_names):
        if not self.client.is_connected():
            self.client.connect()

        keys = [(self.namespace, self.set_aggregated, bucket_name) for bucket_name in bucket_names]
        buckets = self.client.get_many(keys)

        return [bucket for (_, _, bucket) in buckets]

    def put_profile(self, user_profile, gen):
        try:
            if not self.client.is_connected():
                self.client.connect()

            key = (self.namespace, self.set, user_profile.cookie)

            buys = snappy.compress(json.dumps([b.model_dump() for b in user_profile.buys], default=str))
            views = snappy.compress(json.dumps([v.model_dump() for v in user_profile.views], default=str))

            meta = {'gen': gen}
            policy = ({'gen': aerospike.POLICY_GEN_EQ})
            bins = {'buys': buys, 'views': views}

            self.client.put(key, bins, meta=meta, policy=policy)
            return True

        except aerospike.exception.RecordGenerationError:
            return False

        except aerospike.exception.AerospikeError as e:
            print(f'Error {e} while trying to write to Aerospike. User cookie: {UserProfile.cookie}')
            return False
