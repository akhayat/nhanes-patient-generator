import logging
import sys
from patient_generator.db_scripts import db_tool

db_tool = db_tool.DBTool()

def generate_name(ethnicity, gender):
    with db_tool.cursor() as cursor:
        cursor.execute(db_tool.query('random_name'), [ethnicity, gender])
        result = cursor.fetchone()
        return result
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    name = generate_name(sys.argv[1], sys.argv[2])
    logging.debug("Generated name: %s", name)