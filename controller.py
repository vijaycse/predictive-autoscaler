import os
from db import get_forecast_next_run, get_forecast_last_run
from scaling import resize_cluster


def resize_server_capacity():
    forecast = get_forecast_next_run()

    if(forecast is not None and len(forecast) > 0):
        if(forecast[1]):  # manual override is enabled
            new_instance_count = get_new_capacity(int(forecast[2]))
        else:
            new_instance_count = get_new_capacity(int(forecast[0]))
    else:  # if no data found, get the last known value
        forecast = get_forecast_last_run()
        new_instance_count = get_new_capacity(int(forecast[0]))
    
    print("new cluster size in each region",new_instance_count)
    resize_cluster(new_instance_count)

def get_new_capacity(forecast):
    print("forecast",forecast)
    new_capacity = None
    if forecast in range(0, 40000):
        new_capacity = 8
    elif forecast in range(40001, 100001):
        new_capacity = 10
    elif forecast in range(100001, 200001):
        new_capacity = 12
    elif forecast in range(200001, 300001):
        new_capacity = 14
    elif forecast in range(300001, 400001):
        new_capacity = 16
    elif forecast in range(400001, 500001):
        new_capacity = 18
    elif forecast in range(500001, 600001):
        new_capacity = 20
    else:
        new_capacity = None

    print("new_capacity per region",new_capacity)
    return int(new_capacity)


if __name__ == '__main__':
    resize_server_capacity()
