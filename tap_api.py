import requests
from config import CLOUD_URL, CLOUD_APPLICATION, CLOUD_SERVER_GROUP,CLOUD_CLUSTER
import time


def resize_cluster(new_instance_count):
    print("Updating cluster")
    min_capacity = 2
    if(new_instance_count > min_capacity):
        session = fetch_session()
        current_instance_count = fetch_current_cluster(session)
        if(new_instance_count != current_instance_count):
            scaling_needed_perct = percentage_change(
                new_instance_count, current_instance_count)
            scaling_diff = new_instance_count - current_instance_count
            if(abs(scaling_needed_perct) > 0.2):  # scale only if diff % more than 20
                # batch it and call method scale cluster iteratively
                for i in range(round(abs(scaling_diff)/5)): # to avoud scaling more than 5 at a time
                    resizing_cluster(i, session)
            else:
                print("No need to scale")
        else:
            print("No need to scale")

        print('Update completed')
    else:
        print('no change needed')


def fetch_session():
    session = requests.Session()
    session.headers['Content-Type'] = 'application/json'
    token_response = session.post(url=CLOUD_URL+'/login',
                                  json={'username': '********',
                                        'password': '*******'},
                                  verify=False)
    session


def fetch_current_cluster(session):
    cluster_info = session.get(url=CLOUD_URL+'/api/applications/'+CLOUD_APPLICATION+'/clusters/'+CLOUD_CLUSTER+'/dev/server_groups/'+CLOUD_SERVER_GROUP,
                               verify=False)
    print(cluster_info.json())
    return cluster_info['instanceCounts']


def resizing_cluster(new_instance_count, session):

    print('resizing Capacity')
    resize_central = session.put(url=CLOUD_URL+'/api/applications/'+CLOUD_APPLICATION+'/clusters/'+CLOUD_CLUSTER+'/dev/server_groups/'+CLOUD_SERVER_GROUP+'/resize',
                                 json={'region': 'us-central1', 'desired': new_instance_count,
                                       'min': '2', 'max': new_instance_count},
                                 verify=False)
    print('resizing central' + resize_central)

    resize_east = session.put(url=CLOUD_URL+'/api/applications/'+CLOUD_APPLICATION+'/clusters/'+CLOUD_CLUSTER+'/dev/server_groups/'+CLOUD_SERVER_GROUP+'resize',
                              json={'region': 'us-east1', 'desired': new_instance_count,
                                    'min': '2', 'max': new_instance_count},
                              verify=False)
    print('resizing central' + resize_east)
    time.sleep(1000)


def percentage_change(new_instance_count, current_instance_count):
    return (new_instance_count - current_instance_count)/current_instance_count


if __name__ == '__main__':
    resize_cluster()
