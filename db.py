from sqlalchemy import create_engine
from sqlalchemy.orm import close_all_sessions
from datetime import date
from config import POSTGRES_ADDRESS, POSTGRES_USERNAME, POSTGRES_PASSWORD, POSTGRES_DBNAME, POSTGRES_PORT
from dateutil.relativedelta import relativedelta
from targetoss_tappy import Configuration
import targetoss_tappy as tappy
import logging
class DB:

    def __init__(self, config):
        self.config = config



    def get_forecast_next_run(self):
        """ query near future estimated order count from the oph_forecast table.
        this returns only (one row) the next possible forecast count """
        db_host,db_name,db_user,db_password,db_port = self.fetch_db_details()
        postgres_str = ('postgresql://{username}:{password}@{ipaddress}:{port}/{dbname}'
                        .format(username=db_user, password=db_password, ipaddress=db_host, port=db_port, dbname=db_name))

        engine = create_engine(postgres_str)
        current_dt = date.today()
        next_dt = date.today() + relativedelta(days=+1)
        logging.info("next day {} ".format(next_dt))
        sql = "SELECT yhat,manual_override,override_order_per_hr FROM oph_forecast where ds>{} and ds<{} ORDER BY ds DESC LIMIT 1;".format(
            "'"+str(current_dt)+"'", "'"+str(next_dt)+"'")
        # sql = "select yhat,manual_override,override_order_per_hr  where ds>{}from oph_forecast order by ds DESC  limit 1"
        result = engine.execute(sql)
        # logging.info(result.fetchone()) # always comment this out when running the script
        return result.fetchone()


    def get_forecast_last_run(self):
        """ query near future estimated order count from the oph_forecast table. 
        this returns only (one row) the last known count """
        db_host,db_name,db_user,db_password,db_port = self.fetch_db_details()
        postgres_str = ('postgresql://{username}:{password}@{ipaddress}:{port}/{dbname}'
                        .format(username=db_user, password=db_password, ipaddress=db_host, port=db_port, dbname=db_name))

        engine = create_engine(postgres_str)
        logging.info("looking for default ")
        sql = "SELECT yhat FROM oph_forecast where manual_override = false ORDER BY ds DESC LIMIT 1;"
        # sql = "select yhat,manual_override,override_order_per_hr  where ds>{}from oph_forecast order by ds DESC  limit 1"
        result = engine.execute(sql)
        # logging.info(result.fetchone()) # always comment this out when running the script
        return result.fetchone()

    def fetch_db_details(self):
        if(self.config and tappy.in_tap()):
            db_details = self.config["db"]
            db_host = db_details["address"]
            db_name = db_details["dbname"]
            db_user = db_details["user"]
            db_password = self.config["db_password"]
            db_port = db_details["port"]
        else:
            db_user = POSTGRES_USERNAME
            db_port = POSTGRES_PORT
            db_password = POSTGRES_PASSWORD
            db_host = POSTGRES_ADDRESS
            db_name = POSTGRES_DBNAME
        return db_host,db_name,db_user,db_password,db_port

    if __name__ == '__main__':
        get_forecast_next_run()
