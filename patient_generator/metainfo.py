# Description: Get information about NHANES tables
from psycopg2.extras import RealDictCursor
from patient_generator import db_utils

db_interface = db_utils.DBTool()

def table_info():
    with db_interface.get_connection().cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(db_interface.query('table_info'))
        return cursor.fetchall()