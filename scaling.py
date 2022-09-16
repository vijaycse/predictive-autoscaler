import requests
from config import CLOUD_URL, CLOUD_APPLICATION, CLOUD_SERVER_GROUP, CLOUD_CLUSTER, CLOUD_USER, CLOUD_PASSWORD
import time

# scale up or down 4 instances at a time


def resize_cluster_batch(new_instance_count, current_instance_count, session, configuration_data=dict()):
    for i in range(1, round(abs(new_instance_count/4))):
        resizing_cluster(((4 * i) + current_instance_count), session,configuration_data)
    print('Update completed')


def resize_cluster(new_instance_count, configuration_data=dict()):
    print("Updating cluster with new capacity per region", new_instance_count)
    min_capacity = 2
    if(new_instance_count is not None):
        new_instance_count = round(new_instance_count)  # central and east
        if(new_instance_count > min_capacity):
            session = fetch_session(configuration_data)
            current_instance_count = fetch_current_cluster(
                session)/2  # total count by region
            print("current instance count ", current_instance_count)
            if(new_instance_count != current_instance_count):
                scaling_perct = percentage_change(
                    new_instance_count, current_instance_count)
                print("diff_perct", scaling_perct)
                scaling_diff = new_instance_count - current_instance_count
                print("scaling_diff", scaling_diff)
                if(scaling_perct > 0.50):  # scale only if diff % more than 0.5%
                    # batch it and call method scale cluster iteratively
                    # to avoid scaling more than 4 at a time with buffer 2
                    resize_cluster_batch(
                        new_instance_count + 2, current_instance_count, session, configuration_data)  # buffer added
                # only do scale up if diff is less than 1%
                elif(scaling_perct <= -1.0 and scaling_diff < 0):  # negative numbers
                    # no need to scale down if less than 1%
                    print("only scaling down")
                    resize_cluster_batch(new_instance_count, 0, session ,configuration_data)
                else:
                    print("No need to scale as difference is not much")
            else:
                print("No need to scale - proposed instance count is same as old")

        else:
            print('no change needed', new_instance_count)
    else:
        print('no change needed', new_instance_count)


def fetch_session(configuration_data=dict()):
    if(configuration_data):
        tap_details = configuration_data["tap"]
        CLOUD_URL = tap_details["url"]
        CLOUD_USER = tap_details["user"]
        CLOUD_PASSWORD = configuration_data["tap_password"]

    requests.packages.urllib3.disable_warnings()
    session = requests.Session()
    session.headers['Content-Type'] = 'application/json'
    token_response = session.post(url=CLOUD_URL+'/login',
                                  json={'username': CLOUD_USER,
                                        'password': CLOUD_PASSWORD},
                                  verify=False)
    # print("token",token_response)
    return session

# TODO: fetch list of all server groups to get the active one. remove hard coded value


def fetch_current_cluster(session, configuration_data=dict()):
    if(configuration_data):
        tap_details = configuration_data["tap"]
        CLOUD_APPLICATION = tap_details["app"]
        CLOUD_CLUSTER = tap_details["cluster"]
        CLOUD_SERVER_GROUP = tap_details["server_group"]

    cluster_info = session.get(url=CLOUD_URL+'/api/applications/'+CLOUD_APPLICATION+'/clusters/'+CLOUD_CLUSTER+'/dev/server_groups/'+CLOUD_SERVER_GROUP,
                               verify=False)
    # print(cluster_info.json()['instanceCounts']['total'])
    return int(cluster_info.json()['instanceCounts']['total'])


def resizing_cluster(new_instance_count, session, configuration_data=dict()):
    if(configuration_data):
        tap_details = configuration_data["tap"]
        CLOUD_APPLICATION = tap_details["app"]
        CLOUD_CLUSTER = tap_details["cluster"]
        CLOUD_SERVER_GROUP = tap_details["server_group"]

    print('resizing Capacity', str(new_instance_count))
    resize_central = session.put(url=CLOUD_URL+'/api/applications/'+CLOUD_APPLICATION+'/clusters/'+CLOUD_CLUSTER+'/dev/server_groups/'+CLOUD_SERVER_GROUP+'/resize',
                                 json={'region': 'us-central1', 'desired': new_instance_count,
                                       'min': '2', 'max': new_instance_count},
                                 verify=False)
    print('resizing central' + str(resize_central))

    resize_east = session.put(url=CLOUD_URL+'/api/applications/'+CLOUD_APPLICATION+'/clusters/'+CLOUD_CLUSTER+'/dev/server_groups/'+CLOUD_SERVER_GROUP+'/resize',
                              json={'region': 'us-east1', 'desired': new_instance_count,
                                    'min': '2', 'max': new_instance_count},
                              verify=False)
    print('resizing east' + str(resize_east))
    time.sleep(20)


def percentage_change(new_instance_count, current_instance_count):
    divider = min(new_instance_count, current_instance_count)
    return (new_instance_count - current_instance_count)/divider


if __name__ == '__main__':
    resize_cluster()
