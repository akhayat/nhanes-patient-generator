import logging
import sys
from patient_generator.db_scripts import db_utils

db_tool = db_utils.DBTool()

def generate_name(ethnicity, gender):
    with db_tool.cursor() as cursor:
        cursor.execute(db_tool.query('random_name'), [ethnicity, gender])
        result = cursor.fetchone()
        return result
    
if __name__ == '__main__':
    name = generate_name(sys.argv[1], sys.argv[2])
    print(f"Generated name: {name}")