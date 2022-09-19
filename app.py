from targetoss_tappy import Configuration
import targetoss_tappy as tappy
from controller import resize_server_capacity
from datetime import datetime


# this func needs no-arg.. so had to fetch tap config again.
def scheduleScalingTask():
    print("job started..")
    if tappy.in_tap():
        config = tappy.Configuration().data
    else:
        config = Configuration()
 
    resize_server_capacity(config)


if __name__ == '__main__':
   # app.config.from_object(Config())  
    scheduleScalingTask()