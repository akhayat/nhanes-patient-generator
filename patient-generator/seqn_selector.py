# Script to get a survey respondent by a random SEQN to use
# for default values for the patient generator

import json
import logging
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from decouple import config

QUERIES = {
    'random_seqn': sql.SQL("SELECT seqn, table_suffix FROM pool.nhanes_patient_seqn ORDER BY random() LIMIT 1"),

    'get_tables': sql.SQL("SELECT table_name FROM information_schema.key_column_usage WHERE column_name = 'SEQN' AND "
                          "table_catalog = {db_name} AND table_schema = 'Translated' AND table_name ILIKE %s"),

    'get_data': sql.SQL('SELECT * FROM "Translated".{table_name} WHERE "SEQN" = %s'),

    'get_sas_labels': sql.SQL('SELECT "Variable" variable, "SasLabel" sas_label FROM "Metadata"."QuestionnaireVariables" '
                      'WHERE "Variable" NOT LIKE \'SEQN\' AND "TableName" = %s and "SasLabel" IS NOT NULL')
}

def get_connection(): 
    try:
        connection = psycopg2.connect(dbname=config('DB_NAME'), user=config('DB_USER'), host=config('DB_HOST'), password=config('DB_PASS'))
        return connection
    except:
        logging.error(f"Unable to connect to database {config('DB_NAME')}")

def random_seqn(cursor):
    cursor.execute(QUERIES['random_seqn'])
    result = cursor.fetchone()
    logging.info(f"Selected SEQN: {result['seqn']} with table suffix: {result['table_suffix']}")
    return result

def get_tables(cursor, table_suffix):
    cursor.execute(QUERIES['get_tables'].format(db_name=sql.Literal(config('DB_NAME'))), [('%' + table_suffix) if table_suffix else '']), 
    result = cursor.fetchall()
    logging.info(f"%d tables found", len(result))
    return result

def get_all_data_for_seqn(cursor, table_list, seqn):
    patient = {}
    logging.debug("table_list = %s" % table_list)
    for table in table_list:
        table_name = table['table_name']
        cursor.execute(QUERIES['get_data'].format(table_name=sql.Identifier(table_name)), [seqn])
        if cursor.rowcount > 0:
            logging.debug(f"table = %s" % table_name)
            patient[table_name] = cursor.fetchone()
            cursor.execute(QUERIES['get_sas_labels'], [table_name])
            labels = cursor.fetchall()
            for label in labels:
                if label['variable'] in patient[table_name]:
                    patient[table_name][label['variable']] = {'description': label['sas_label'], 'value': patient[table_name][label['variable']]}
                else:
                    logging.debug(f"Column {label['variable']} not found in table {table_name}")
        else:
            logging.debug(f"No data found for SEQN {seqn} in table {table_name}")
    return patient

def generate_random_patient_as_json(file_name):
    with get_connection().cursor(cursor_factory=RealDictCursor) as cursor:
        seqn = random_seqn(cursor)
        table_list = get_tables(cursor, seqn['table_suffix'])
        patient = get_all_data_for_seqn(cursor, table_list, seqn['seqn'])
        with open(file_name, 'w') as file:
            json.dump(patient, file, indent = 4)
            logging.info(f"Patient data written to {file_name}")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    generate_random_patient_as_json('patient.json')
