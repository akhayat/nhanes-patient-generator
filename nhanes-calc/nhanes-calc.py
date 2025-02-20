# Script to calculate the count and percent of total for each value
# in the NHANES database when given a table and column 
import logging
import psycopg2
from psycopg2 import sql
from decouple import config

QUERIES = {
    "calc_exists": sql.SQL("SELECT COUNT(*) FROM pool.nhanes_data_pool WHERE ref_table ILIKE %s AND ref_column ILIKE %s "),

    "calc_insert": sql.SQL("INSERT INTO pool.nhanes_data_pool (value, count, total, ref_table, ref_column, field_name) "
        "SELECT {column}, count(*), (SELECT count(*) FROM \"Translated\".{table}), {table_name}, {column_name}, {sas_label} "
        "FROM \"Translated\".{table} group by {column}"),

    "get_variables": "SELECT \"TableName\", \"Variable\", \"SasLabel\" FROM \"Metadata\".\"QuestionnaireVariables\" "
         "WHERE \"Variable\" NOT LIKE 'SEQN' AND \"SasLabel\" IS NOT NULL LIMIT %s OFFSET %s"
}

SELECT_LIMIT = 50

def nhanes_calc():
    try:
        connection = psycopg2.connect(dbname=config('DB_NAME'), user=config('DB_USER'), host=config('DB_HOST'), password=config('DB_PASS'))
    except:
      logging.error(f"Unable to connect to database {config('DB_NAME')}")

    with connection.cursor() as cursor:
        offset = 0
        variables = nhanes_get_variables(cursor, SELECT_LIMIT, offset) 
        while len(variables) > 0:
            for variable in variables:
                table = variable[0]
                column = variable[1]
                sas_label = variable[2]
                if nhanes_calc_exists(cursor, table, column):
                    logging.info(f"Skipping calculation for {table}.{column} as it already exists")
                else:
                    nhanes_calc_insert(cursor, table, column, sas_label)
                    connection.commit()
            offset += SELECT_LIMIT
            variables = nhanes_get_variables(cursor, SELECT_LIMIT, offset)

def nhanes_calc_exists(cursor, table, column):
    cursor.execute(QUERIES['calc_exists'], [table, column])
    total = cursor.fetchone()[0]
    return total > 0


def nhanes_calc_insert(cursor, table, column, sas_label):
    try: 
        cursor.execute(QUERIES['calc_insert'].format(column=sql.Identifier(column), table=sql.Identifier(table), 
                column_name=sql.Literal(column), table_name=sql.Literal(table), sas_label=sql.Literal(sas_label)))
        logging.debug(f"{cursor.rowcount} rows migrated from {table}.{column}")
    except Exception as e:
        logging.error(f"Error migrating {table}.{column}: {e}")

def nhanes_get_variables(cursor, limit, offset):
    cursor.execute(QUERIES['get_variables'], [limit, offset])
    return cursor.fetchall()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    nhanes_calc()
