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
    sql = "SELECT yhat FROM oph_forecast where ds>{} ORDER BY ds DESC LIMIT 1;".format("'"+current_ts+"'")
    result = engine.execute(sql)
    #print(result.fetchone()[0]) // always comment this out when running the script
    return result.fetchone()[0]


if __name__ == '__main__':
    get_forecast_next_run()
