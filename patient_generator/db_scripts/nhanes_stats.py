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
from patient_generator.db_scripts import db_utils

db_tool = db_utils.DBTool()

def data_for_variable(table_name, variable):
    with db_tool.cursor(cursor_factory=RealDictCursor) as cursor:
        result = []
        cursor.execute(db_tool.query('data_counts_by_variable').format(table=sql.Literal(table_name), variable=sql.Literal(variable)))
        for row in cursor.fetchall():
            if row['ValueDescription'] != 'Missing' and row['Count'] > 0:
                if row['ValueDescription'] == 'Range of Values':
                    range = re.split(r' to ', row['CodeOrValue'])
                    min, max = range[0], range[1]
                    row['stats'] = stats(data_for_range(table_name, variable, min, max))
                result.append(row)
        return result

def stats(data):
    return {
        "mean": statistics.mean(data), 
        "stdev": statistics.stdev(data), 
        "median": statistics.median(data), 
        "mode": statistics.mode(data), 
        "variance": statistics.variance(data),
        "quartiles": statistics.quantiles(data, n=4, method='inclusive')
    }


def data_for_range(table_name, variable, min_value, max_value):
    with db_tool.cursor() as cursor:
        cursor.execute(db_tool.query('data_for_range').format(variable=sql.Identifier(variable), table=sql.Identifier(table_name)), [min_value, max_value])
        return [row[0] for row in cursor.fetchall()]
    
def data_as_json(table_name, variable):
    return json.dumps(data_for_variable(table_name, variable), indent=4)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    table_name, variable = sys.argv[1], sys.argv[2]
    logging.info("Stats for %s: %s", table_name, data_as_json(table_name, variable))
