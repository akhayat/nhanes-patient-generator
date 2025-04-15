# Script for retrieving data from a given dataset (table) and variable (column)
# from a PostgreSQL database containing NHANES survey data from the CDC
# It then returns the count for each variable if discrete, and, if it
# contains a continuous range of data, calculates the
# standard, deviation, median, mode, variance, and quartiles.
# Returns the result as a list of JSON objects

import json
import logging
import re
import statistics
import sys
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from patient_generator.db_scripts import db_tool

db_tool = db_tool.DBTool()

def data_for_variable(table_name, variable, adults_only=False, gender=None):
    with db_tool.cursor(cursor_factory=RealDictCursor) as cursor:
        result = []
        demo_table = db_tool.demo_table(table_name)
        cursor.execute(db_tool.query('data_counts_by_variable').format(table=sql.Literal(table_name), 
                variable=sql.Literal(variable), demo_table=sql.Identifier(demo_table)), [variable])
        
        for row in cursor.fetchall():
            camelized_row = row.copy()
            camelized_row = db_tool.camelize_keys(camelized_row)
            if camelized_row['valueDescription'] != 'Missing' and camelized_row['count'] > 0:
                if camelized_row['valueDescription'] == 'Range of Values':
                    range = re.split(r' to ', camelized_row['codeOrValue'])
                    min, max = range[0], range[1]
                    camelized_row['stats'] = stats(table_name, demo_table, variable, min, max, adults_only, gender)
                result.append(camelized_row)
        return result

def stats(table_name, demo_table, variable, min, max, adults_only, gender):
    data = data_for_range(table_name, demo_table, variable, min, max, adults_only, gender)
    stat_block = {"count": len(data)}
    if stat_block["count"] > 0:
        stat_block = stat_block |{
            "mean": statistics.mean(data), 
            "stdev": statistics.stdev(data), 
            "median": statistics.median(data), 
            "mode": statistics.mode(data), 
            "variance": statistics.variance(data),
            "quartiles": statistics.quantiles(data, n=4, method='inclusive')
        }
        if adults_only:
            stat_block['adults_only'] = True
        if gender is not None:
            stat_block['gender'] = gender
    return stat_block


def data_for_range(table_name, demo_table, variable, min_value, max_value, adults_only=False, gender=None):
    with db_tool.cursor() as cursor:
        query = db_tool.query('data_for_range').format(variable=sql.Identifier(variable), table=sql.Identifier(table_name))
        if table_name != demo_table:
            query += db_tool.join('demo').format(demo_table=sql.Identifier(demo_table))
        query +=  sql.SQL(' WHERE ') + db_tool.conditions('variable_range').format(variable=sql.Identifier(variable))
        conditions = sql.SQL(' ')

        args = [min_value, max_value]
        if adults_only:
            conditions += db_tool.conditions('adults_only')
        if gender is not None:
            conditions += db_tool.conditions('gender')
            args.append('Male' if gender.lower() == 'm' else 'Female')
        if conditions.as_string(cursor).strip():
            query += conditions.join(' AND ')
        
        logging.debug("QUERY: %s", query.as_string(cursor))
        cursor.execute(query, args)
        return [row[0] for row in cursor.fetchall()]
    
def data_as_json(table_name, variable, adults_only=False, gender=None):
    return json.dumps(data_for_variable(table_name, variable, adults_only, gender), indent=4)

def parse_adults_only_from_args(argv):
    return len(argv) >= 4 and 'adults_only' == argv[3].lower() or len(argv) == 5 and 'adults_only' == argv[4].lower()

def parse_gender_from_args(argv):
    gender_regex = re.compile(r'm|M|f|F')
    return argv[3] if len(argv) >= 4 and gender_regex.match(argv[3]) else argv[4] if len(argv) == 5 and gender_regex.match(argv[4]) else None

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    table_name, variable = sys.argv[1], sys.argv[2]
    adults_only, gender = parse_adults_only_from_args(sys.argv), parse_gender_from_args(sys.argv)

    logging.info("Stats for %s: %s", table_name, data_as_json(table_name, variable, adults_only, gender))
