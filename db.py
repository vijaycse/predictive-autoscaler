from sqlalchemy import create_engine
from sqlalchemy.orm import close_all_sessions
from datetime import date
from config import POSTGRES_ADDRESS, POSTGRES_USERNAME, POSTGRES_PASSWORD, POSTGRES_DBNAME ,POSTGRES_PORT
from dateutil.relativedelta import relativedelta

def get_forecast_next_run(configuration_data=dict()):
    """ query near future estimated order count from the oph_forecast table. 
    this returns only (one row) the next possible forecast count """

    if(configuration_data):
        db_details = conf.data["db"]
        POSTGRES_ADDRESS = db_details["address"]
        POSTGRES_DBNAME = db_details["dbname"]
        POSTGRES_USERNAME = db_details["user"]
        POSTGRES_PASSWORD = db_details["password"]
        POSTGRES_PORT = db_details["port"]

    postgres_str = ('postgresql://{username}:{password}@{ipaddress}:{port}/{dbname}'
    .format(username=POSTGRES_USERNAME,password=POSTGRES_PASSWORD,ipaddress=POSTGRES_ADDRESS,port=POSTGRES_PORT,dbname=POSTGRES_DBNAME))

    engine = create_engine(postgres_str)
    current_dt = date.today()
    next_dt = date.today() + relativedelta(days=+1)
    print("next day",next_dt)
    sql = "SELECT yhat,manual_override,override_order_per_hr FROM oph_forecast where ds>{} and ds<{} ORDER BY ds DESC LIMIT 1;".format("'"+str(current_dt)+"'", "'"+str(next_dt)+"'")
    #sql = "select yhat,manual_override,override_order_per_hr  where ds>{}from oph_forecast order by ds DESC  limit 1"
    result = engine.execute(sql)
    #print(result.fetchone()) # always comment this out when running the script
    return result.fetchone()


def get_forecast_last_run(configuration_data=dict()):
    """ query near future estimated order count from the oph_forecast table. 
    this returns only (one row) the last known count """

    if(configuration_data):
        db_details = conf.data["db"]
        POSTGRES_ADDRESS = db_details["address"]
        POSTGRES_DBNAME = db_details["dbname"]
        POSTGRES_USERNAME = db_details["user"]
        POSTGRES_PASSWORD = db_details["password"]
        POSTGRES_PORT = db_details["port"]

    postgres_str = ('postgresql://{username}:{password}@{ipaddress}:{port}/{dbname}'
    .format(username=POSTGRES_USERNAME,password=POSTGRES_PASSWORD,ipaddress=POSTGRES_ADDRESS,port=POSTGRES_PORT,dbname=POSTGRES_DBNAME))

    engine = create_engine(postgres_str)
    sql = "SELECT yhat FROM oph_forecast where manual_override = false ORDER BY ds DESC LIMIT 1;"
    #sql = "select yhat,manual_override,override_order_per_hr  where ds>{}from oph_forecast order by ds DESC  limit 1"
    result = engine.execute(sql)
    #print(result.fetchone()) # always comment this out when running the script
    return result.fetchone()

if __name__ == '__main__':
    get_forecast_next_run()
