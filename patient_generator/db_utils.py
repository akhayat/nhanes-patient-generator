
import logging
import psycopg2
from psycopg2 import sql
from decouple import config

QUERIES = {
    'random_seqn': sql.SQL("SELECT seqn, table_suffix FROM pool.nhanes_patient_seqn ORDER BY random() LIMIT 1"),

    'tables': sql.SQL("SELECT table_name FROM information_schema.key_column_usage WHERE column_name = 'SEQN' AND "
                          "table_catalog = {db_name} AND table_schema = 'Translated' AND table_name ILIKE %s"),
                
    'tables_null_suffix': sql.SQL("SELECT table_name FROM information_schema.key_column_usage WHERE column_name = 'SEQN' AND "
                          "table_catalog = {db_name} AND table_schema = 'Translated' AND table_name NOT LIKE '%\\__'"),

    'data_for_seqn': sql.SQL('SELECT * FROM "Translated".{table_name} WHERE "SEQN" = %s'),

    'sas_labels': sql.SQL('SELECT "Variable" variable, "SasLabel" sas_label FROM "Metadata"."QuestionnaireVariables" '
                      'WHERE "Variable" NOT LIKE \'SEQN\' AND "TableName" = %s and "SasLabel" IS NOT NULL'),

    'data_counts_by_variable': sql.SQL('SELECT qv."Variable", qv."TableName", "CodeOrValue", "Count", "ValueDescription", "SasLabel", "Target" '
                                        'FROM "Metadata"."VariableCodebook" vc INNER JOIN "Metadata"."QuestionnaireVariables" qv '
                                        'ON (vc."TableName" = qv."TableName" and vc."Variable" = qv."Variable") '
                                        'WHERE qv."TableName" ILIKE {table} AND qv."Variable" ILIKE {variable}'),

    'data_for_range': sql.SQL('SELECT {variable} FROM "Translated".{table} WHERE {variable} >= %s AND {variable} <= %s'),

    'table_info': sql.SQL('SELECT "TableName", "DatePublished", "DocFile", "Description" '
                          'FROM "Metadata"."QuestionnaireDescriptions" ORDER BY "EndYear" DESC, "TableName" ASC')
}

class DBInterface:
    def __init__(self):
        pass

    def get_connection(self): 
        try:
            return psycopg2.connect(dbname=config('DB_NAME'), user=config('DB_USER'), host=config('DB_HOST'), password=config('DB_PASS'))
        except:
            logging.error(f"Unable to connect to database {config('DB_NAME')}")

    def query(self, query_name):
        return QUERIES[query_name]
