import schedule
from controller.controller import resize_server_capacity

def pull_latest_forecast():
    print("started querying data")
    resize_server_capacity()

schedule.every(60).minute.do(pull_latest_forecast)

def trigger_job():
    while True:
        schedule.run_pending()

if __name__=='__main__':
    trigger_job()
