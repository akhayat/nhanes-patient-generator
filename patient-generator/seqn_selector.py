# Script to get a survey respondent by a random SEQN to use
# for default values for the patient generator
import logging
import psycopg2
from psycopg2 import sql
from decouple import config

QUERIES = {
    "random_seqn": sql.SQL("SELECT seqn, table_suffix FROM pool.nhanes_patient_seqn ORDER BY random() LIMIT 1"),

    "get_tables": sql.SQL("SELECT table_name FROM information_schema.tables "
                          "WHERE database = {db_name} AND table_schema = 'Translated' AND table_name ILIKE '%{suffix}'"),

    "get_variables": "SELECT \"TableName\", \"Variable\", \"SasLabel\" FROM \"Metadata\".\"QuestionnaireVariables\" "
         "WHERE \"Variable\" NOT LIKE 'SEQN' AND \"SasLabel\" IS NOT NULL LIMIT %s OFFSET %s"
}

def get_connection(): 
    try:
        connection = psycopg2.connect(dbname=config('DB_NAME'), user=config('DB_USER'), host=config('DB_HOST'), password=config('DB_PASS'))
        return connection
    except:
      logging.error(f"Unable to connect to database {config('DB_NAME')}")

def random_seqn(cursor):
        cursor.execute(QUERIES["random_seqn"])
        seqn, table_suffix = cursor.fetchone()
        logging.info(f"Selected SEQN: {seqn} with table suffix: {table_suffix}")

def get_tables(cursor,table_suffix):
    return None

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    with get_connection().cursor() as cursor:
        random_seqn(cursor)
    