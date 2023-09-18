import sys
import pymysql
import os
from dotenv import load_dotenv
load_dotenv()


class Component():
    @staticmethod
    def get_connection() -> pymysql.connections.Connection:
        return pymysql.connect(
            host=os.getenv('RDS_HOSTNAME'),
            user=os.getenv('RDS_USERNAME'),
            password=os.getenv('RDS_PASSWORD'),
        )

    @staticmethod
    def getDetailsByComponentId(component_id):
        try:
            connection = Component.get_connection()
            cursor = connection.cursor()
            sql_query = "SELECT name, component_type, component_category, testing_framework, api_type FROM component.component_view WHERE component_id = %s"
            cursor.execute(sql_query, (component_id))
            result = cursor.fetchone()
            return result
        except Exception as e:
            print("Exception catched " + str(e), file=sys.stderr)
            return None
