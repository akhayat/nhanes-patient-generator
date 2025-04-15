# Description: Get information about NHANES tables
from psycopg2.extras import RealDictCursor
from patient_generator.db_scripts import db_tool

db_tool = db_tool.DBTool()

def table_info():
    with db_tool.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(db_tool.query('table_info'))
        return db_tool.camelize_keys(cursor.fetchall())