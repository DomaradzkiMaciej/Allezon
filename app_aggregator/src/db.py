from types_ import Aggregate

import aerospike
from aerospike_helpers.operations import operations


class AerospikeClient:
    namespace = 'allezon'
    set = 'aggregated'

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

    def close(self):
        self.client.close()

    def put_aggregated(self, bucket_name, count, sum_price):
        try:
            if not self.client.is_connected():
                self.client.connect()

            key = (self.namespace, self.set, bucket_name)
            operations_list = [operations.increment(Aggregate.COUNT.value, count),
                               operations.increment(Aggregate.SUM_PRICE.value, sum_price)]

            self.client.operate(key, operations_list)
            return True

        except aerospike.exception.AerospikeError as e:
            print(f'Error {e} while trying to write to Aerospike.')
            return False
