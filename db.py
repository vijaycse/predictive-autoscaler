from sqlalchemy import create_engine
from sqlalchemy.orm import close_all_sessions
from datetime import datetime
from config import POSTGRES_ADDRESS, POSTGRES_USERNAME, POSTGRES_PASSWORD, POSTGRES_DBNAME ,POSTGRES_PORT

def get_forecast_next_run():
    """ query near future estimated order count from the oph_forecast table. 
    this returns only (one row) the next possible forecast count """

    postgres_str = ('postgresql://{username}:{password}@{ipaddress}:{port}/{dbname}'
    .format(username=POSTGRES_USERNAME,password=POSTGRES_PASSWORD,ipaddress=POSTGRES_ADDRESS,port=POSTGRES_PORT,dbname=POSTGRES_DBNAME))

    engine = create_engine(postgres_str)
    current_ts =  str(datetime.utcnow())
    print(current_ts)
    sql = "SELECT yhat,manual_override,override_order_per_hr FROM oph_forecast where ds>{} ORDER BY ds DESC LIMIT 1;".format("'"+current_ts+"'")
    #sql = "select yhat,manual_override,override_order_per_hr  where ds>{}from oph_forecast order by ds DESC  limit 1"
    result = engine.execute(sql)
    #print(result.fetchone()[0]) # always comment this out when running the script
    return result.fetchone()


def get_forecast_last_run():
    """ query near future estimated order count from the oph_forecast table. 
    this returns only (one row) the last known count """

    postgres_str = ('postgresql://{username}:{password}@{ipaddress}:{port}/{dbname}'
    .format(username=POSTGRES_USERNAME,password=POSTGRES_PASSWORD,ipaddress=POSTGRES_ADDRESS,port=POSTGRES_PORT,dbname=POSTGRES_DBNAME))

    engine = create_engine(postgres_str)
    current_ts =  str(datetime.utcnow())
    print(current_ts)
    sql = "SELECT yhat,manual_override,override_order_per_hr FROM oph_forecast ORDER BY ds DESC LIMIT 1;".format("'"+current_ts+"'")
    #sql = "select yhat,manual_override,override_order_per_hr  where ds>{}from oph_forecast order by ds DESC  limit 1"
    result = engine.execute(sql)
    #print(result.fetchone()[0]) # always comment this out when running the script
    return result.fetchone()

if __name__ == '__main__':
    get_forecast_next_run()
