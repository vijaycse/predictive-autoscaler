import requests
from config import CLOUD_URL, CLOUD_APPLICATION, CLOUD_SERVER_GROUP, CLOUD_CLUSTER, CLOUD_USER, CLOUD_PASSWORD, CLOUD_ENVIRONMENT, CLOUD_APPLICATION_SECONDARY, CLOUD_CLUSTER_SECONDARY
from config import OAUTH_CLIENT_ID,OAUTH_CLIENT_SECRET,OAUTH_PASSWORD,OAUTH_URL,OAUTH_USER_NAME
from config import ALERT_API_KEY , ALERT_TOKEN
import time
from targetoss_tappy import Configuration
import targetoss_tappy as tappy
import os
import math
import logging
from common import post_payload, post_service_alert
import scaling

# scale up or down 4 instances at a time


class Scaling:

    min_capacity = 50

    def __init__(self, config):
        self.config = config
        self.tap_app, self.tap_cluster, self.tap_env, self.tap_url, self.tap_user, self.tap_password, self.tap_app_secondary, self.tap_cluster_secondary = self.fetch_tap_details(
            config)

    def resize_cluster_batch(self, new_instance_count, current_instance_count, session, server_group, app, cluster):
        logging.info('scaling need for {} , new instance - {} ,current instance count - {}'.format(
            app, new_instance_count, current_instance_count))
        if(new_instance_count <= 4):
            new_instance_count = 5  # setting atleast 5 min
        for i in range(1, math.ceil(abs(new_instance_count/4))):
            self.resizing_cluster(((4 * i) + current_instance_count),
                                  session, server_group, app, cluster)
        logging.info('Update completed for {}'.format(app))
        print('Update completed for {}'.format(app))
        oauth_config = self.fetch_oauth_details(self.config)
        alert_api , alert_token = self.fetch_alert_details(self.config)
        post_service_alert(
            'Scaling completed for {}'.format(app), self.tap_env,alert_api, alert_token , oauth_config)

    def resize_cluster(self, new_instance_count):
        print("Updating cluster with new capacity per region", new_instance_count)
        logging.info(
            "Updating cluster with new capacity per region", new_instance_count)
        if(self.tap_env == 'dev'):   # if this is dev, just cut down to quarter resources
            new_instance_count = round(new_instance_count/4)
            Scaling.min_capacity = round(Scaling.min_capacity/4)
            logging.info("dev instance count ", new_instance_count)
        if(new_instance_count is not None):
            new_instance_count = round(new_instance_count)
            if(new_instance_count > Scaling.min_capacity):
                session = self.fetch_session()
                server_group, current_instance_count = self.fetch_current_cluster(
                    session, self.tap_app, self.tap_cluster)
                current_instance_count = current_instance_count/2  # total count need by region
                logging.info("current instance count ", current_instance_count)
                if(new_instance_count != current_instance_count):
                    scaling_perct = self.percentage_change(
                        new_instance_count, current_instance_count)
                    logging.info("diff_perct", scaling_perct)
                    scaling_diff = new_instance_count - current_instance_count
                    print("scaling_diff", scaling_diff)
                    logging.info("scaling_diff", scaling_diff)
                    if(scaling_perct > 0.50):  # scale only if diff % more than 0.5%
                        # batch it and call method scale cluster iteratively
                        # to avoid scaling more than 4 at a time with buffer 2
                        self.resize_cluster_batch(
                            new_instance_count, current_instance_count, session, server_group, self.tap_app, self.tap_cluster)

                        server_group, current_instance_count = self.fetch_current_cluster(
                            session, self.tap_app_secondary, self.tap_cluster_secondary)

                        self.resize_cluster_batch(  # secondary instance count reduce by 10
                            math.ceil(new_instance_count / 10), (current_instance_count), session, server_group, self.tap_app_secondary, self.tap_cluster_secondary)  # buffer added
                    # only do scale up if diff is less than 1%
                    elif(scaling_perct <= -1.0 and scaling_diff < 0):  # negative numbers
                        # no need to scale down if less than 1%
                        logging.info("only scaling down")

                        self.resize_cluster_batch(
                            new_instance_count, 0, session, server_group, self.tap_app, self.tap_cluster)

                        server_group, current_instance_count = self.fetch_current_cluster(
                            session, self.tap_app_secondary, self.tap_cluster_secondary)

                        self.resize_cluster_batch(  # secondary instance count reduce by 10
                            math.ceil(new_instance_count / 10), 0, session, server_group, self.tap_app_secondary, self.tap_cluster_secondary)
                    else:
                        logging.info(
                            "No need to scale as difference is not much")
                else:
                    logging.info(
                        "No need to scale - proposed instance count is same as old")

            else:
                logging.info('no change needed', new_instance_count)
        else:
            logging.info('no change needed', new_instance_count)

    def fetch_session(self):
        requests.packages.urllib3.disable_warnings()
        session = requests.Session()
        session.headers['Content-Type'] = 'application/json'
        token_response = session.post(url=self.tap_url+'/login',
                                      json={'username': self.tap_user,
                                            'password': self.tap_password},
                                      verify=False)
        # logging.info("token",token_response)
        return session

    def fetch_server_group(self, session, app, cluster):
        server_group_info = session.get(url=self.tap_url+'/api/applications/'+app+'/clusters/'+cluster+'/'+self.tap_env+'/server_groups/',
                                        verify=False)
        return server_group_info.json()['data'][0]['name']

    def fetch_current_cluster(self, session, app, cluster):
        tap_server_group = self.fetch_server_group(session, app, cluster)
        logging.info(" fetching current cluster app {} , cluster {} , server_group {}".format(
            app, cluster, tap_server_group))
        cluster_info = session.get(url=self.tap_url+'/api/applications/'+app+'/clusters/'+cluster+'/'+self.tap_env+'/server_groups/'+tap_server_group,
                                   verify=False)
        # logging.info(cluster_info.json())
        return tap_server_group, int(cluster_info.json()['instanceCounts']['total'])

    def resizing_cluster(self, new_instance_count, session, server_group, app, cluster):
        logging.info('resizing Capacity', str(new_instance_count))
        logging.info(" resizing Capacity cluster app {} , cluster {} , server_group {}".format(
            app, cluster, server_group))
        resize_central = session.put(url=self.tap_url+'/api/applications/'+app+'/clusters/'+cluster+'/dev/server_groups/'+server_group+'/resize',
                                     json={'region': 'us-central1', 'desired': new_instance_count,
                                           'min': Scaling.min_capacity, 'max': new_instance_count},
                                     verify=False)
        logging.info('resizing central' + str(resize_central))

        resize_east = session.put(url=self.tap_url+'/api/applications/'+app+'/clusters/'+cluster+'/dev/server_groups/'+server_group+'/resize',
                                  json={'region': 'us-east1', 'desired': new_instance_count,
                                        'min': Scaling.min_capacity, 'max': new_instance_count},
                                  verify=False)
        logging.info('resizing east' + str(resize_east))
        time.sleep(20)

    def percentage_change(self, new_instance_count, current_instance_count):
        divider = min(new_instance_count, current_instance_count)
        return (new_instance_count - current_instance_count)/divider

    def fetch_tap_details(self, configuration_data):
        if(configuration_data and tappy.in_tap()):
            tap_details = configuration_data["tap"]
            tap_url = tap_details["url"]
            tap_app = tap_details["app"]
            tap_cluster = tap_details["cluster"]
            tap_env = os.getenv('CLOUD_ENVIRONMENT')
            tap_user = tap_details["user"]
            tap_password = configuration_data["tap_password"]
            tap_app_secondary = tap_details["app_secondary"]
            tap_cluster_secondary = tap_details["cluster_secondary"]
        else:
            tap_app = CLOUD_APPLICATION
            tap_cluster = CLOUD_CLUSTER
            tap_url = CLOUD_URL
            tap_env = CLOUD_ENVIRONMENT
            tap_user = CLOUD_USER
            tap_password = CLOUD_PASSWORD
            tap_app_secondary = CLOUD_APPLICATION_SECONDARY
            tap_cluster_secondary = CLOUD_CLUSTER_SECONDARY
        return tap_app, tap_cluster, tap_env, tap_url, tap_user, tap_password, tap_app_secondary, tap_cluster_secondary

    def fetch_oauth_details(self, configuration_data):
        oauth_info = {}
        if(configuration_data and tappy.in_tap()):
            oauth_details = configuration_data["oauth"]
            oauth_info['url'] = oauth_details["url"]
            oauth_info['user_name'] = oauth_details["user_name"]
            oauth_info['client_id'] = oauth_details["client_id"]
            oauth_info['password'] = configuration_data('oauth_password')
            oauth_info['client_secret'] = configuration_data('oauth_client_secret')
        else:
            oauth_info['url'] =  OAUTH_URL
            oauth_info['user_name']  = OAUTH_USER_NAME
            oauth_info['client_id'] = OAUTH_CLIENT_ID
            oauth_info['password'] = OAUTH_PASSWORD
            oauth_info['client_secret'] = OAUTH_CLIENT_SECRET
        return oauth_info


    def fetch_alert_details(self, configuration_data):
        if(configuration_data and tappy.in_tap()):
            alert_details = configuration_data["alert"]
            alert_api_key = alert_details["api_key"]
            alert_token = configuration_data('alert_token')
        else:
            alert_api_key = ALERT_API_KEY
            alert_token = ALERT_TOKEN
          
        return alert_api_key , alert_token

    if __name__ == '__main__':
        scale = Scaling(config=dict())
        oauth_config = scale.fetch_oauth_details({})
        post_service_alert(
            'Scaling completed for {}'.format(app), self.tap_env, oauth_config)
