from logging.config import fileConfig
from flask import Flask, jsonify
from targetoss_tappy import Configuration
import targetoss_tappy as tappy
from flask_apscheduler import APScheduler
from controller import resize_server_capacity
from datetime import datetime
import logging

app = Flask(__name__)

scheduler = APScheduler()

@app.route('/health')
def health():
    return jsonify({'status': 'up'})


@app.route('/')
def index():
    logging.info("hello - this is logging!")
    return jsonify({'time': datetime.now()})


@app.route('/config')
def config():
    if tappy.in_tap():
        config = tappy.Configuration().data
    else:
        config = Configuration()
    logging.info("config ",config)
    return jsonify(conf.get("job", "config_value isn't in Consul!"))


def scheduleScalingTask():
    if tappy.in_tap():
        config = tappy.Configuration().data
    else:
        config = Configuration()
    logging.info("Jobs started")
    resize_server_capacity(config)

def job():
    if tappy.in_tap():
        config = tappy.Configuration().data
        job_details = config["job"]
        job_hr = job_details["hour"]
        job_min = job_details["minute"]
    else:
        config = Configuration()
        job_hr = 12
        job_min = 32

    scheduler.add_job(id='Scheduled Task1', func=scheduleScalingTask,
                      trigger="cron", hour=int(job_hr), minute=int(job_min))
    if not scheduler.running:
        scheduler.start()
    logging.info("Job scheduler initiated {} {} ".format(job_hr , job_min))



if __name__ == '__main__':
   # app.config.from_object(Config())
    scheduler.init_app(app)    
    job()
    app.run(debug=False, use_reloader=False, host='0.0.0.0', port=8080)