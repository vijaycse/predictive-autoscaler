import requests
from config import CLOUD_URL, CLOUD_APPLICATION, CLOUD_SERVER_GROUP, CLOUD_CLUSTER, CLOUD_USER, CLOUD_PASSWORD
import time


def resize_cluster(new_instance_count):
    print("Updating cluster")
    min_capacity = 2
    new_instance_count = 10
    if(new_instance_count is not None):
        new_instance_count = round(new_instance_count)
        if(new_instance_count > min_capacity):
            session = fetch_session()
            current_instance_count = fetch_current_cluster(session)
            if(new_instance_count != current_instance_count):
                    scaling_needed_perct = percentage_change(
                        new_instance_count, current_instance_count)
                    print("perct",scaling_needed_perct)
                    scaling_diff = new_instance_count - current_instance_count
                    print("scaling_diff",scaling_diff)
                    if(abs(scaling_needed_perct) > 2.0):  # scale only if diff % more than 2%
                            # batch it and call method scale cluster iteratively
                            # to avoud scaling more than 5 at a time
                            for i in range(round(abs(scaling_diff)/5)):
                                resizing_cluster(5, session)
                            print('Update completed')
                    else:
                        print("No need to scale")
            else:
                print("No need to scale")

        else:
            print('no change needed')
    else:
        print('no change needed')


def fetch_session():
    session = requests.Session()
    session.headers['Content-Type'] = 'application/json'
    token_response = session.post(url=CLOUD_URL+'/login',
                                  json={'username': CLOUD_USER,
                                        'password': CLOUD_PASSWORD},
                                  verify=False)
    print("token",token_response)
    return session

##TODO: fetch list of all server groups to get the active one. remove hard coded value
def fetch_current_cluster(session):
    cluster_info = session.get(url=CLOUD_URL+'/api/applications/'+CLOUD_APPLICATION+'/clusters/'+CLOUD_CLUSTER+'/dev/server_groups/'+CLOUD_SERVER_GROUP,
                               verify=False)
    print(cluster_info.json())
    return cluster_info.json()['instanceCounts']['total']


def resizing_cluster(new_instance_count, session):

    print('resizing Capacity', str(new_instance_count))
    # resize_central = session.put(url=CLOUD_URL+'/api/applications/'+CLOUD_APPLICATION+'/clusters/'+CLOUD_CLUSTER+'/dev/server_groups/'+CLOUD_SERVER_GROUP+'/resize',
    #                              json={'region': 'us-central1', 'desired': new_instance_count,
    #                                    'min': '2', 'max': new_instance_count},
    #                              verify=False)
    # print('resizing central' + str(resize_central))

    # resize_east = session.put(url=CLOUD_URL+'/api/applications/'+CLOUD_APPLICATION+'/clusters/'+CLOUD_CLUSTER+'/dev/server_groups/'+CLOUD_SERVER_GROUP+'resize',
    #                           json={'region': 'us-east1', 'desired': new_instance_count,
    #                                 'min': '2', 'max': new_instance_count},
    #                           verify=False)
    # print('resizing east' + str(resize_east))
    # time.sleep(1000)


def percentage_change(new_instance_count, current_instance_count):
     divider = min(new_instance_count, current_instance_count)
     return (new_instance_count - current_instance_count)/divider


if __name__ == '__main__':
    resize_cluster()