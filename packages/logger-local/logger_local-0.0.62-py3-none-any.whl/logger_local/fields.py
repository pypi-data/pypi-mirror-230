    
import sys
import pymysql
import os
from dotenv import load_dotenv
from .SendToLogzIo import SendTOLogzIo
from .MessageSeverity import MessageSeverity
load_dotenv()

FIELDS_LIST=None
COMPUTER_LANGUAGE = "Python"
COMPONENT_ID = 102
COMPONENT_NAME = 'Logger Python'
Logzio_handler=SendTOLogzIo()

def get_connection() -> pymysql.connections.Connection:
            return pymysql.connect(
                host=os.getenv('RDS_HOSTNAME'),
                user=os.getenv('RDS_USERNAME'),
                password=os.getenv('RDS_PASSWORD'),
                
            )
class Fields:
    def __init__(self) -> None:
        pass


    @staticmethod
    def getFieldsSingelton():
        if FIELDS_LIST is None:
            try:
                object1 = {
                'record': {'severity_id': MessageSeverity.Information.value, 'severity_name': MessageSeverity.Information.name, 'component_id': COMPONENT_ID, 'component_name': COMPONENT_NAME, 'computer_language': COMPUTER_LANGUAGE, 'message': "get_logger_table_fields activated"},
                'severity_id': MessageSeverity.Information.value,
                'component_id': COMPONENT_ID,
                'severity_name': MessageSeverity.Information.name,
                'component_name': COMPONENT_NAME,
                'COMPUTER_LANGUAGE': COMPUTER_LANGUAGE,
                'message': "get_logger_table_fields activated",
            }
                Logzio_handler.send_to_logzio(object1)
                con =get_connection()
                cursor = con.cursor()
                sql_query = f"DESCRIBE logger.logger_table"
                cursor.execute(sql_query)
                columns_info = cursor.fetchall()
                Fields = [column[0] for column in columns_info]
            except Exception as e:
                print("logger-local-python-package LoggerService.py sql(self) Exception catched SQL=" +
                    sql_query+" Exception=" + str(e), file=sys.stderr)
                return None
        return Fields