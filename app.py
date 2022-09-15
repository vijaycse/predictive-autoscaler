from logging.config import fileConfig
from flask import Flask, jsonify
from targetoss_tappy import Configuration
from jobscheduler import job
import targetoss_tappy as tappy

# fileConfig('logging.conf')
app = Flask(__name__)


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


if __name__ == '__main__':
    conf = Configuration()
    job(conf.data)
    app.run(debug=False, use_reloader=False, host='0.0.0.0', port=8080)
