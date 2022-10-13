import os
from db import DB
from scaling import Scaling
import logging
from config import EXPECTED_OPH_FOR_100K,EXPECTED_OPH_FOR_50K,EXPECTED_OPH_FOR_200K,EXPECTED_OPH_FOR_300K,EXPECTED_OPH_FOR_400K,EXPECTED_OPH_FOR_500K,EXPECTED_OPH_FOR_600K


def resize_server_capacity(configuration_data=dict()):
    db  = DB(configuration_data)
    forecast = db.get_forecast_next_run()

    if(forecast is not None and len(forecast) > 0):
        if(forecast[1]):  # manual override is enabled
            new_instance_count = get_new_capacity(int(forecast[2]))
        else:
            new_instance_count = get_new_capacity(int(forecast[0]))
    else:  # if no data found, get the last known value
        logging.info(" no schedule found, resetting to default value")
        forecast = db.get_forecast_last_run()
        new_instance_count = get_new_capacity(int(forecast[0]))
    
    logging.info("new cluster size in each region {} ".format(new_instance_count))
    scaling = Scaling(configuration_data)
    scaling.resize_cluster(new_instance_count)

##TODO: need to get this mapping from config
## OPH /TPS is total regardless of the regions. we need to divide the number by region
## e.g 300K OPH -> 300/2  150K perr region
def get_new_capacity(forecast):
    logging.info("forecast {} ".format(forecast))
    forcast_per_region = round(forecast/2)
    new_capacity = None
    if forcast_per_region in range(0, 50001):
        new_capacity = EXPECTED_OPH_FOR_50K
    elif forcast_per_region in range(50001, 100001):
        new_capacity = EXPECTED_OPH_FOR_100K
    elif forcast_per_region in range(100001, 200001):
        new_capacity = EXPECTED_OPH_FOR_200K
    elif forcast_per_region in range(200001, 300001):
        new_capacity = EXPECTED_OPH_FOR_300K
    elif forcast_per_region in range(300001, 400001):
        new_capacity = EXPECTED_OPH_FOR_400K
    elif forcast_per_region in range(400001, 500001):
        new_capacity = EXPECTED_OPH_FOR_500K
    elif forcast_per_region in range(500001, 600001):
        new_capacity = EXPECTED_OPH_FOR_600K
    else:
        new_capacity = 200

    logging.info("new_capacity per region {} ".format(new_capacity))
    return int(new_capacity)


if __name__ == '__main__':
    resize_server_capacity()
