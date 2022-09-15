from apscheduler.triggers.multi import OrTrigger
from controller import resize_server_capacity
from logging.config import fileConfig
from flask_apscheduler import APScheduler


scheduler = APScheduler()


def scheduleScalingTask(configuration_data):
    resize_server_capacity(configuration_data)


def job(configuration_data=dict()):
    if(conf.data):
        job_details = conf.data["job"]
        job_hr = job_details["hour"]
        job_minute = job_details["minute"]
    else:
        job_hr = 1
        job_minute = 20

    app.logger.info("Job scheduler details {} {} ".format(job_hr, job_minute))
    # add more jobs bot_scanner job later
    trigger = OrTrigger([CronTrigger(hour=job_hr, minute=job_minute)])
    scheduler.add_job(scheduleScalingTask(configuration_data), trigger)
    scheduler.start()
