# Script to calculate the count and percent of total for each value
# in the NHANES database when given a table and column name
import psycopg2
from psycopg2 import sql
from decouple import config

queries = {
    "calc_exists": sql.SQL("SELECT COUNT(*) FROM pool.nhanes_data_pool WHERE ref_table ILIKE %s AND ref_column ILIKE %s "),

    "calc_insert": sql.SQL("INSERT INTO pool.nhanes_data_pool (value, count, total, ref_table, ref_column, field_name) "
        "SELECT {column}, count(*), (SELECT count(*) FROM \"Translated\".{table}), {table_name}, {column_name}, \"SasLabel\" "
        "FROM \"Translated\".{table} INNER JOIN \"Metadata\".\"QuestionnaireVariables\" ON (\"Variable\" ILIKE {column_name} AND \"TableName\" ILIKE {table_name}) "
        "group by {column}, \"SasLabel\"")
}

def nhanes_calc(table, column):
    try:
        connection = psycopg2.connect(dbname=config('DB_NAME'), user=config('DB_USER'), host=config('DB_HOST'), password=config('DB_PASS'))
    except:
      print(f"Unable to connect to database {config('DB_NAME')}")

    with connection.cursor() as cursor:
        if nhanes_calc_exists(cursor, table, column):
            print(f"Skipping calculation for {table}.{column} as it already exists")
        else:
            nhanes_calc_insert(cursor, table, column)
            connection.commit()


def nhanes_calc_exists(cursor, table, column):
    cursor.execute(queries['calc_exists'], [table, column])
    total = cursor.fetchone()[0]
    return total > 0


def nhanes_calc_insert(cursor, table, column):
    cursor.execute(queries['calc_insert'].format(column=sql.Identifier(column), table=sql.Identifier(table), 
            column_name=sql.Literal(column), table_name=sql.Literal(table)))
    print(f"{cursor.rowcount} rows migrated from {table}.{column}")

if __name__ == '__main__':
    nhanes_calc('DEMO_L','DMDMARTZ')
    nhanes_calc('DEMO_L','RIAGENDR')
