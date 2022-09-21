import requests
import logging

from oauth import getauth

# reuse connections. using requests.sessions
session = None


def post_payload(uri, payload, header={}, auth=None):
    logging.debug(" payload {} , uri {} ".format(payload, uri))
    session = get_session()
    return session.post(uri,
                        verify=False,
                        json=payload,
                        headers=header,
                        auth=auth
                        )


def get_session():
    global session
    if(session):
        return session
    else:
        logging.info("Creating a new connection ")
        session = requests.Session()
        return session


def post_service_alert(msg, env,alert_api, alert_token,oauth_config=dict()):
    payload = {"status":msg,"env":env}
    print("payload", payload)
    mytoken = getauth(oauth_config)
    alert_resp = post_payload("https://api.target.com/service_alerts/v1/?scope_token={}&key={}".format(alert_token,alert_api),
                             payload,
                             {'Authorization': 'Bearer '+mytoken}
                             )
    logging.info("alert payload response".format(payload))
    if alert_resp.status_code != 200:
        # This means something went wrong.
        logging.error(
            'POST /alert_msg/ for {}, status is {}'.format(payload, alert_resp.status_code))
    else:
        logging.info(
            " alert req successful for  {}".format(payload))
