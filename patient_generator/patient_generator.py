# Script to get a survey respondent by a random SEQN to use
# for default values for the patient generator

import json
import logging
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from decouple import config
from patient_generator import db_utils

def random_seqn(cursor):
    cursor.execute(db_utils.query('random_seqn'))
    result = cursor.fetchone()
    logging.info(f"Selected SEQN: {result['seqn']} with table suffix: {result['table_suffix']}")
    return result

def get_tables(cursor, table_suffix):
    if table_suffix == None:
        cursor.execute(db_utils.query('tables_null_suffix').format(db_name=sql.Literal(config('DB_NAME'))))
    else:
        cursor.execute(db_utils.query('tables').format(db_name=sql.Literal(config('DB_NAME'))), [('%' + table_suffix) if table_suffix else '']), 
    result = cursor.fetchall()
    logging.debug(f"%d tables found", len(result))
    return result

def get_all_data_for_seqn(cursor, table_list, seqn):
    patient = {}
    for table in table_list:
        table_name = table['table_name']
        cursor.execute(db_utils.query('data_for_seqn').format(table_name=sql.Identifier(table_name)), [seqn])
        if cursor.rowcount > 0:
            logging.debug(f"table = %s" % table_name)
            table_data = cursor.fetchone()
            cursor.execute(db_utils.query('sas_labels'), [table_name])
            labels = cursor.fetchall()
            patient[table_name] = {}
            for variable in table_data:
                if table_data[variable] != None:
                    label = next((item for item in labels if item['variable'] == variable), None)
                    patient[table_name][variable] = {"variable": table_data[variable], "description": None if not label else label['sas_label']}
        else:
            logging.debug(f"No data found for SEQN {seqn} in table {table_name}")
    return patient

def generate_random_patient():
    with db_utils.get_connection().cursor(cursor_factory=RealDictCursor) as cursor:
        seqn = random_seqn(cursor)
        table_list = get_tables(cursor, seqn['table_suffix'])
        return get_all_data_for_seqn(cursor, table_list, seqn['seqn'])


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    patient = generate_random_patient()
    file_name = './examples/patient.json'
    with open(file_name, 'w') as file:
        json.dump(patient, file, indent = 4)
        logging.info(f"Patient data written to {file_name}")
