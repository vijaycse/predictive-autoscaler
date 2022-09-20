import requests
from requests.auth import HTTPBasicAuth
import urllib.parse
import json
import os


def getauth(config):
    # Set URL
    # Prod https://oauth.iam.target.com
    # Stage https://oauth.iam.perf.target.com
    oauth_props = config
    url = oauth_props['url']

    # Create dictionary of parameters
    params = {'grant_type': 'password',
              'username': oauth_props['user_name'],
              'password': oauth_props['password']
              }

    params['scope'] = 'profile email openid'

    # Set the headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    # Make the request
    response = requests.post(
        url, headers=headers, data=params, auth=HTTPBasicAuth(oauth_props['client_id'], oauth_props['client_secret']), verify=False)

    if response.status_code != 200:
        # This means something went wrong.
        print('POST /oauth/ {}'.format(response.status_code))
    else:
        print(" oauth req successful")
        # Extract the access token from the json response
        parsedJson = json.loads(response.text)
        access_token = parsedJson['access_token']

    return access_token
