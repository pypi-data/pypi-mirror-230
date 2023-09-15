import random

import time
from prometheus_client import Summary
from prometheus_client import Gauge
from prometheus_client import start_http_server

# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')


# Decorate function with metric.
# @REQUEST_TIME.time()
def process_request(t):
    """A dummy function that takes some time."""
    time.sleep(t)


g = Gauge('my_inprogress_requests', 'Description of gauge')
g.inc()      # Increment by 1
g.dec(10)    # Decrement by given value
g.set(4.2)   # Set to a given value


@REQUEST_TIME.time()
def get_data():
    x = random.randint(0, 99)
    print(f"{x = }")
    return x


d = Gauge('data_objects', 'Number of objects')
my_dict = {}
d.set_function(get_data)

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)
    # Generate some requests.
    while True:
        process_request(random.random())
