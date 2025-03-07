# Description: Get information about NHANES tables
from psycopg2.extras import RealDictCursor
from decouple import config
from patient_generator import db_utils

def table_info():
    with db_utils.get_connection().cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(db_utils.query('table_info'))
        return cursor.fetchall()