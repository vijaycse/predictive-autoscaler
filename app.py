from logging.config import fileConfig
from flask import Flask, jsonify
from targetoss_tappy import Configuration
import targetoss_tappy as tappy
from flask_apscheduler import APScheduler
from controller import resize_server_capacity
from datetime import datetime
from apscheduler.triggers.cron import CronTrigger 
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

scheduler = BackgroundScheduler()

@app.route('/health')
def health():
    return jsonify({'status': 'up'})


@app.route('/')
def index():
    app.logger.info("hello - this is logging!")
    return jsonify({'time': datetime.now()})


@app.route('/config')
def config():
    if tappy.in_tap():
        conf = tappy.Configuration().data
    else:
        conf = Configuration()

    app.logger.info(conf)
    return jsonify(conf.get("job", "config_value isn't in Consul!"))

# this func needs no-arg.. so had to fetch tap config again.
def scheduleScalingTask():
    if tappy.in_tap():
        config = tappy.Configuration().data
    else:
        config = Configuration()
 
    resize_server_capacity(config)

#@scheduler.task('cron', id='do_job_1', hour=8, minute='30')
def schedule_job():
    if tappy.in_tap():
        config = tappy.Configuration().data
        job_details = config["job"]
        job_hr = job_details["hour"]
        job_min = job_details["minute"]
    else:
        config = Configuration()
        job_hr = 13
        job_min = 55

    scheduler.add_job(scheduleScalingTask, 'cron', day_of_week ='mon-sun', hour=job_hr, minute=job_min)
    scheduler.start()
    app.logger.info("Job scheduler details ")


if __name__ == '__main__':
   # app.config.from_object(Config())  
    schedule_job()
    app.run(debug=False, use_reloader=False, host='0.0.0.0', port=8080)