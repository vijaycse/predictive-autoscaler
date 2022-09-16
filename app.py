from logging.config import fileConfig
from flask import Flask, jsonify
from targetoss_tappy import Configuration
import targetoss_tappy as tappy
from flask_apscheduler import APScheduler

app = Flask(__name__)

scheduler = APScheduler()

@app.route('/health')
def health():
    return jsonify({'status': 'up'})


@app.route('/')
def index():
    app.logger.info("hello - this is logging!")
    return jsonify({'status': 'up'})


@app.route('/config')
def config():
    conf = Configuration()
    app.logger.info(conf.data)
    return jsonify(conf.data.get("cart", "config_value isn't in Consul!"))


def scheduleScalingTask(configuration_data):
    resize_server_capacity(configuration_data)



@scheduler.task('cron', id='do_job_1', hour=0, minute='1')
def job(configuration_data=dict()):
    conf = Configuration()
    if(conf.data):
        job_details = conf.data["job"]
        job_hr = job_details["hour"]
        job_minute = job_details["minute"]
    else:
        job_hr = 1
        job_minute = 20

    app.logger.info("Job scheduler details {} {} ".format(job_hr, job_minute))
    # add more jobs bot_scanner job later
    scheduleScalingTask(configuration_data)

if __name__ == '__main__':
    conf = Configuration()
   # app.config.from_object(Config())
    scheduler.init_app(app)
    scheduler.start()

    app.run()
    app.run(debug=False, use_reloader=False, host='0.0.0.0', port=8080)
