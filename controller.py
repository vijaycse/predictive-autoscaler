import os
from db import get_forecast_next_run
from tap_api import resize_cluster


def resize_server_capacity():
    forecast = get_forecast_next_run()
    new_instance_count = get_new_capacity(forecast)
    resize_cluster(new_instance_count)

def get_new_capacity(forecast):
    new_capacity = None
    if forecast in range(0, 40000):
        new_capacity = 3
    elif forecast in range(40001, 100000):
        new_capacity = 4
    elif forecast in range(100001, 200000):
        new_capacity = 5
    elif forecast in range(200001, 300000):
        new_capacity = 6
    elif forecast in range(300001, 400000):
        new_capacity = 7
    elif forecast in range(400001, 500000):
        new_capacity = 8
    elif forecast in range(500001, 600000):
        new_capacity = 9
    else:
        new_capacity = None

    return new_capacity


if __name__ == '__main__':
    resize_server_capacity()
