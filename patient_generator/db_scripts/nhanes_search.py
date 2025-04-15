import json
import logging
import sys
from psycopg2.extras import RealDictCursor
from psycopg2 import sql

from patient_generator.db_scripts import db_tool

db_tool = db_tool.DBTool()

def search(search_query, limit=50): 
    with db_tool.cursor(cursor_factory=RealDictCursor) as cursor:
        ts_query = search_query.strip().replace(' ', ' | ')
        cursor.execute(db_tool.query('search').format(query=sql.Literal(ts_query)), [limit])
        results = cursor.fetchall()
        list(map(lambda item: db_tool.camelize_keys(item), results))
        return results
    
def data_as_json(search_query, limit=50):
    return json.dumps(search(search_query, limit), indent=4)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    search_query, limit = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None
    results = search_query, data_as_json(search_query, limit) if limit != None else data_as_json(search_query)
    logging.info(f"Items matching terms: %s", results)