import requests
from config import CLOUD_URL, CLOUD_APPLICATION, CLOUD_SERVER_GROUP, CLOUD_CLUSTER, CLOUD_USER, CLOUD_PASSWORD, CLOUD_ENVIRONMENT, CLOUD_APPLICATION_SECONDARY, CLOUD_CLUSTER_SECONDARY
import time
from targetoss_tappy import Configuration
import targetoss_tappy as tappy
import os
import math

# scale up or down 4 instances at a time


class Scaling:

    min_capacity = 50

    def __init__(self, config):
        self.tap_app,self.tap_cluster,self.tap_env,self.tap_url,self.tap_user,self.tap_password,self.tap_app_secondary,self.tap_cluster_secondary = self.fetch_tap_details(config)

    def resize_cluster_batch(self, new_instance_count, current_instance_count, session, server_group, app , cluster):
        print('scaling need for {} , new instance - {} ,current instance count - {}'.format(app,new_instance_count, current_instance_count))
        if(new_instance_count <= 4):
            new_instance_count = 5  #setting atleast 5 min
        for i in range(1, math.ceil(abs(new_instance_count/4))):
            self.resizing_cluster(((4 * i) + current_instance_count),
                                  session, server_group, app, cluster)
        print('Update completed for {}'.format(app))

    def resize_cluster(self, new_instance_count):
        print("Updating cluster with new capacity per region", new_instance_count)
        if(self.tap_env == 'dev'):   # if this is dev, just cut down to quarter resources
            new_instance_count = round(new_instance_count/4)
            Scaling.min_capacity = round(Scaling.min_capacity/4)
            print("dev instance count ", new_instance_count)
        if(new_instance_count is not None):
            new_instance_count = round(new_instance_count)
            if(new_instance_count > Scaling.min_capacity):
                session = self.fetch_session()
                server_group, current_instance_count = self.fetch_current_cluster(
                    session, self.tap_app, self.tap_cluster)
                current_instance_count = current_instance_count/2  # total count need by region
                print("current instance count ", current_instance_count)
                if(new_instance_count != current_instance_count):
                    scaling_perct = self.percentage_change(
                        new_instance_count, current_instance_count)
                    print("diff_perct", scaling_perct)
                    scaling_diff = new_instance_count - current_instance_count
                    print("scaling_diff", scaling_diff)
                    if(scaling_perct > 0.50):  # scale only if diff % more than 0.5%
                        # batch it and call method scale cluster iteratively
                        # to avoid scaling more than 4 at a time with buffer 2
                        self.resize_cluster_batch(
                            new_instance_count , current_instance_count, session, server_group, self.tap_app, self.tap_cluster)   
                        server_group, current_instance_count = self.fetch_current_cluster(session, self.tap_app_secondary, self.tap_cluster_secondary)
                        self.resize_cluster_batch(  # secondary instance count reduce by 10
                            math.ceil(new_instance_count / 10), (current_instance_count), session, server_group, self.tap_app_secondary, self.tap_cluster_secondary)  # buffer added
                    # only do scale up if diff is less than 1%
                    elif(scaling_perct <= -1.0 and scaling_diff < 0):  # negative numbers
                        # no need to scale down if less than 1%
                        print("only scaling down")
                        self.resize_cluster_batch(
                            new_instance_count, 0, session, server_group, self.tap_app, self.tap_cluster)
                        self.resize_cluster_batch(  # secondary instance count reduce by 10
                            math.ceil(new_instance_count / 10), 0, session, server_group, self.tap_app_secondary, self.tap_cluster_secondary)
                    else:
                        print("No need to scale as difference is not much")
                else:
                    print("No need to scale - proposed instance count is same as old")

            else:
                print('no change needed', new_instance_count)
        else:
            print('no change needed', new_instance_count)

    def fetch_session(self):
        requests.packages.urllib3.disable_warnings()
        session = requests.Session()
        session.headers['Content-Type'] = 'application/json'
        token_response = session.post(url=self.tap_url+'/login',
                                      json={'username': self.tap_user,
                                            'password': self.tap_password},
                                      verify=False)
        # print("token",token_response)
        return session

    def fetch_server_group(self, session, app, cluster):
        server_group_info = session.get(url=self.tap_url+'/api/applications/'+app+'/clusters/'+cluster+'/'+self.tap_env+'/server_groups/',
                                        verify=False)
        return server_group_info.json()['data'][0]['name']

    def fetch_current_cluster(self, session, app, cluster):
        tap_server_group = self.fetch_server_group(session, app, cluster)
        print(" fetching current cluster app {} , cluster {} , server_group {}".format(app, cluster,tap_server_group))
        cluster_info = session.get(url=self.tap_url+'/api/applications/'+app+'/clusters/'+cluster+'/'+self.tap_env+'/server_groups/'+tap_server_group,
                                   verify=False)
        #print(cluster_info.json())
        return tap_server_group, int(cluster_info.json()['instanceCounts']['total'])

    def resizing_cluster(self, new_instance_count, session, server_group, app, cluster):
        print('resizing Capacity', str(new_instance_count))
        print(" resizing Capacity cluster app {} , cluster {} , server_group {}".format(app, cluster,server_group))
        resize_central = session.put(url=self.tap_url+'/api/applications/'+app+'/clusters/'+cluster+'/dev/server_groups/'+server_group+'/resize',
                                     json={'region': 'us-central1', 'desired': new_instance_count,
                                           'min': Scaling.min_capacity, 'max': new_instance_count},
                                     verify=False)
        print('resizing central' + str(resize_central))

        resize_east = session.put(url=self.tap_url+'/api/applications/'+app+'/clusters/'+cluster+'/dev/server_groups/'+server_group+'/resize',
                                  json={'region': 'us-east1', 'desired': new_instance_count,
                                        'min': Scaling.min_capacity , 'max': new_instance_count},
                                  verify=False)
        print('resizing east' + str(resize_east))
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
        return tap_app, tap_cluster,tap_env, tap_url,tap_user, tap_password,tap_app_secondary, tap_cluster_secondary

    if __name__ == '__main__':
        scale = Scaling(config=dict())
        scale.resize_cluster(10)
