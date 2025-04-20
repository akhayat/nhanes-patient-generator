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

class NHANESStats:

    def __init__(self, table_name, variable, adults_only=False, gender=None, lazy=False):
        self.db_tool = db_tool.DBTool()
        self.table_name = table_name
        self.variable = variable
        self.adults_only = adults_only
        self.gender = gender
        self.demo_table = self.db_tool.demo_table(table_name)
        self.data = []
        if not lazy:
            self.fetch_data_for_variable()


    def fetch_data_for_variable(self):
        with self.db_tool.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(self.db_tool.query('data_counts_by_variable').format(table=sql.Literal(self.table_name), 
                    variable=sql.Literal(self.variable), demo_table=sql.Identifier(self.demo_table)), [self.variable])
            
            for row in cursor.fetchall():
                if row['ValueDescription'] != 'Missing' and row['Count'] > 0:
                    camelized_row = row.copy()
                    camelized_row = self.db_tool.camelize_keys(camelized_row)
                    if camelized_row['valueDescription'] == 'Range of Values':
                        range = re.split(r' to ', camelized_row['codeOrValue'])
                        min, max = range[0], range[1]
                        stats = self.__stats(min, max)
                        camelized_row['count'] = 0 if stats is None else stats['count']
                        if stats is not None:
                            camelized_row['stats'] = self.__stats(min, max)
                    elif self.adults_only or self.gender is not None:
                        camelized_row['count'] = self.__update_count(camelized_row['codeOrValue'])
                    camelized_row['gender'] = self.gender if self.gender is not None else 'Any'
                    camelized_row['adultsOnly'] = self.adults_only
                    self.data.append(camelized_row)
            return self.data

    def __update_count(self, value):
        with self.db_tool.cursor() as cursor:
            query = self.db_tool.query('count_for_variable').format(variable=sql.Identifier(self.variable), table=sql.Identifier(self.table_name))
            query = self.__join_demo_table(query)
            query += sql.SQL(' WHERE ') + self.db_tool.conditions('variable_value').format(variable=sql.Identifier(self.variable))
            args = [value]
            query = self.__add_conditions(cursor, query, args)
            logging.debug("QUERY: %s", query.as_string(cursor))
            cursor.execute(query, args)
            return cursor.fetchone()[0]
            
            
    def __data_for_range(self, min_value, max_value):
        with self.db_tool.cursor() as cursor:
            query = self.db_tool.query('data_for_range').format(variable=sql.Identifier(self.variable), table=sql.Identifier(self.table_name))
            query = self.__join_demo_table(query)
            query +=  sql.SQL(' WHERE ') + self.db_tool.conditions('variable_range').format(variable=sql.Identifier(self.variable))

            args = [min_value, max_value]
            query = self.__add_conditions(cursor, query, args)

            logging.debug("QUERY: %s", query.as_string(cursor))
            cursor.execute(query, args)
            return [row[0] for row in cursor.fetchall()]
        
    def __stats(self, min, max):
        data_points = self.__data_for_range(min, max)
        count = len(data_points)
        return {
            "count": count,
            "mean": statistics.mean(data_points), 
            "stdev": statistics.stdev(data_points), 
            "median": statistics.median(data_points), 
            "mode": statistics.mode(data_points), 
            "variance": statistics.variance(data_points),
            "quartiles": statistics.quantiles(data_points, n=4, method='inclusive')
        } if count > 0 else None
        
    def __join_demo_table(self, query):
        if self.table_name != self.demo_table:
            query += self.db_tool.join('demo').format(demo_table=sql.Identifier(self.demo_table))
        return query
        
    def __add_conditions(self, cursor, query, args):
        conditions = sql.SQL(' ')
        if self.adults_only:
            conditions += self.db_tool.conditions('adults_only')
        if self.gender is not None:
            conditions += self.db_tool.conditions('gender')
            args.append('Male' if self.gender.lower() == 'm' else 'Female')
        if conditions.as_string(cursor).strip():
            query += conditions.join(' AND ')
        return query
        
    def data_as_json(self):
        return json.dumps(self.data, indent=4)

def parse_adults_only_from_args(argv):
    return len(argv) >= 4 and 'adults_only' == argv[3].lower() or len(argv) == 5 and 'adults_only' == argv[4].lower()

def parse_gender_from_args(argv):
    gender_regex = re.compile(r'm|M|f|F')
    return argv[3] if len(argv) >= 4 and gender_regex.match(argv[3]) else argv[4] if len(argv) == 5 and gender_regex.match(argv[4]) else None

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    table_name, variable = sys.argv[1], sys.argv[2]
    adults_only, gender = parse_adults_only_from_args(sys.argv), parse_gender_from_args(sys.argv)

    logging.info("Stats for %s: %s", table_name, NHANESStats(table_name, variable, adults_only, gender).data_as_json())
