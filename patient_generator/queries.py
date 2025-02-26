from psycopg2 import sql

QUERIES = {
    'random_seqn': sql.SQL("SELECT seqn, table_suffix FROM pool.nhanes_patient_seqn ORDER BY random() LIMIT 1"),

    'get_tables': sql.SQL("SELECT table_name FROM information_schema.key_column_usage WHERE column_name = 'SEQN' AND "
                          "table_catalog = {db_name} AND table_schema = 'Translated' AND table_name ILIKE %s"),
                
    'get_table_null_suffix': sql.SQL("SELECT table_name FROM information_schema.key_column_usage WHERE column_name = 'SEQN' AND "
                          "table_catalog = {db_name} AND table_schema = 'Translated' AND table_name NOT LIKE '%\\__'"),

    'get_data': sql.SQL('SELECT * FROM "Translated".{table_name} WHERE "SEQN" = %s'),

    'get_sas_labels': sql.SQL('SELECT "Variable" variable, "SasLabel" sas_label FROM "Metadata"."QuestionnaireVariables" '
                      'WHERE "Variable" NOT LIKE \'SEQN\' AND "TableName" = %s and "SasLabel" IS NOT NULL')
}

def queries():
    return QUERIES