
import logging
import inflection
from django.db import connections
from psycopg2 import sql
from decouple import config

class DBTool:
    def __init__(self):
        pass

    def cursor(self, cursor_factory=None): 
        try:
            return connections['default'].cursor().connection.cursor(cursor_factory=cursor_factory)
        except Exception as e:
            logging.error(f"Unable to connect to database {config('DB_NAME')}")
            logging.error(f"Error: {e}")

    def query(self, query_name):
        return QUERIES[query_name]
    
    def conditions(self, condition):
        return CONDITIONS[condition]
    
    def join(self, join_name):
        return JOINS[join_name]
    
    def demo_table(self, table_name):
        return 'DEMO' + self.table_suffix(table_name)
    
    def table_suffix(self, table_name):
        suffix = table_name.split('_')
        return ('_' + suffix[-1]) if len(suffix) > 1 else ''
    
    def camelize_keys(self, dict):
        for old_key in list(dict.keys()):
            dict[inflection.camelize(old_key, False)] = dict.pop(old_key)
        return dict

CONDITIONS = {
    "adults_only": sql.SQL('"RIDAGEYR" >= 18'),
    "gender": sql.SQL('"RIAGENDR" = %s'),
    "variable_range": sql.SQL("{variable} >= %s AND {variable} < %s"),
    "by_seqn": sql.SQL('"SEQN" = %s'),
    "variable_value": sql.SQL('{variable} = %s'),
}

JOINS = {
    "demo": sql.SQL('INNER JOIN "Translated".{demo_table} dt ON (dt."SEQN" = t."SEQN")'),
}

QUERIES = {
    'random_seqn': 
        sql.SQL("SELECT seqn, table_suffix FROM pool.nhanes_patient_seqn ORDER BY random() LIMIT 1"),

    'tables': 
        sql.SQL("SELECT table_name FROM information_schema.key_column_usage WHERE column_name = 'SEQN' "
                "AND table_catalog = {db_name} AND table_schema = 'Translated' AND table_name ILIKE %s"),
                
    'tables_null_suffix': 
        sql.SQL("SELECT table_name FROM information_schema.key_column_usage WHERE column_name = 'SEQN' "
                "AND table_catalog = {db_name} AND table_schema = 'Translated' AND table_name NOT LIKE '%\\__'"),

    'data_for_table': 
        sql.SQL('SELECT * FROM "Translated".{table_name}'),

    'sas_labels': 
        sql.SQL('SELECT "Variable" variable, "SasLabel" sas_label FROM "Metadata"."QuestionnaireVariables" '
                'WHERE "Variable" NOT LIKE \'SEQN\' AND "TableName" = %s and "SasLabel" IS NOT NULL'),

    'data_counts_by_variable': 
        sql.SQL('SELECT qv."Variable", qv."TableName", "CodeOrValue", "Count", "ValueDescription", "SasLabel", "Target" '
                'FROM "Metadata"."VariableCodebook" vc INNER JOIN "Metadata"."QuestionnaireVariables" qv '
                'ON (vc."TableName" = qv."TableName" and vc."Variable" = qv."Variable") '
                'WHERE qv."TableName" ILIKE {table} AND qv."Variable" ILIKE {variable}'),

    'data_for_range': 
        sql.SQL('SELECT {variable} FROM "Translated".{table} t '),

    'count_for_variable': 
        sql.SQL('SELECT DISTINCT COUNT({variable}) FROM "Translated".{table} t '),

    'table_info': 
        sql.SQL('SELECT "TableName", "DatePublished", "DocFile", "Description" '
                'FROM "Metadata"."QuestionnaireDescriptions" ORDER BY "EndYear" DESC, "TableName" ASC '),

    'search': 
        sql.SQL('SELECT "Variable", "TableName", "SasLabel", "Description", ts_rank("VariableTSV", to_tsquery({query})) rank '
                'FROM "Metadata"."QuestionnaireVariables" '
                'WHERE "VariableTSV" @@ to_tsquery({query}) ORDER BY rank desc LIMIT %s'),

    'random_name':
        sql.SQL("SELECT first.name first_name, last.name last_name FROM pool.first_name first INNER JOIN pool.last_name last ON (first.ethnicity = last.ethnicity) "
                "WHERE last.ethnicity = %s AND gender = %s ORDER BY random() LIMIT 1")
}

