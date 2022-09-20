from logging.config import fileConfig
from flask import Flask, jsonify
from targetoss_tappy import Configuration
import targetoss_tappy as tappy
from flask_apscheduler import APScheduler
from controller import resize_server_capacity
from datetime import datetime

app = Flask(__name__)

scheduler = APScheduler()

@app.route('/health')
def health():
    return jsonify({'status': 'up'})


@app.route('/')
def index():
    app.logger.info("hello - this is logging!")
    return jsonify({'time': datetime.now()})


@app.route('/config')
def config():
    conf = Configuration()
    app.logger.info(conf.data)
    return jsonify(conf.data.get("cart", "config_value isn't in Consul!"))


def scheduleScalingTask():
    if tappy.in_tap():
        config = tappy.Configuration().data
    else:
        config = Configuration()
    print("Jobs started")
    resize_server_capacity(config)

#@scheduler.task('cron', id='do_job_1', hour=8, minute='30')
def job():
    if tappy.in_tap():
        config = tappy.Configuration().data
        job_details = config["job"]
        job_hr = job_details["hour"]
        job_min = job_details["minute"]
    else:
        config = Configuration()
        job_hr = 19
        job_min = 10

    scheduler.add_job(id='Scheduled Task1', func=scheduleScalingTask,
                      trigger="cron", hour=job_hr, minute=job_min)
    scheduler.start()
    print("Job scheduler initiated{} {} ".format(job_hr , job_min))



if __name__ == '__main__':
   # app.config.from_object(Config())
    scheduler.init_app(app)    
    job()
    app.run(debug=False, use_reloader=False, host='0.0.0.0', port=8080)