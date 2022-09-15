import os
from db import get_forecast_next_run, get_forecast_last_run
from scaling import resize_cluster


def resize_server_capacity(configuration_data=dict()):
    forecast = get_forecast_next_run(configuration_data)

    if(forecast is not None and len(forecast) > 0):
        if(forecast[1]):  # manual override is enabled
            new_instance_count = get_new_capacity(int(forecast[2]))
        else:
            new_instance_count = get_new_capacity(int(forecast[0]))
    else:  # if no data found, get the last known value
        print(" no schedule found, resetting to default value")
        forecast = get_forecast_last_run(configuration_data)
        new_instance_count = get_new_capacity(int(forecast[0]))
    
    print("new cluster size in each region",new_instance_count)
    resize_cluster(new_instance_count,configuration_data)

##TODO: need to get this mapping from config
## OPH /TPS is total regardless of the regions. we need to divide the number by region
## e.g 300K OPH -> 300/2  150K perr region
def get_new_capacity(forecast):
    print("forecast",forecast)
    forcast_per_region = round(forecast/2)
    new_capacity = None
    if forcast_per_region in range(0, 40001):
        new_capacity = 8
    elif forcast_per_region in range(40001, 100001):
        new_capacity = 10
    elif forcast_per_region in range(100001, 200001):
        new_capacity = 12
    elif forcast_per_region in range(200001, 300001):
        new_capacity = 14
    elif forcast_per_region in range(300001, 400001):
        new_capacity = 16
    elif forcast_per_region in range(400001, 500001):
        new_capacity = 18
    elif forcast_per_region in range(500001, 600001):
        new_capacity = 20
    else:
        new_capacity = None

    print("new_capacity per region",new_capacity)
    return int(new_capacity)


if __name__ == '__main__':
    resize_server_capacity()
