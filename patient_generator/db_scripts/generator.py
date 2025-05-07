import logging
import random
from patient_generator.db_scripts import db_tool
from patient_generator.models import AggregatedNhanesData
from patient_generator.models import Patient

db_tool = db_tool.DBTool()

class PatientGenerator:
    def __init__(self):
        self.patient = Patient()
        self.generate()

    @classmethod
    def generate_random(cls):
        return cls().patient
    
    def generate(self):
        self.gender = random.choice(['M', 'F'])
        self.ethnicity = self.generate
        self.name = self.generate_name

    def nhanes_random_value(self, field_name):
        stats = AggregatedNhanesData(table, variable, adultsOnly, gender)

    def generate_gender(self):
        return random.choice(['M', 'F'])
    
    #def generate_race(self):

    
    def generate_name(ethnicity, gender):
        with db_tool.cursor() as cursor:
            cursor.execute(db_tool.query('random_name'), [ethnicity, gender])
            result = cursor.fetchone()
            return result
     

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    patient = PatientGenerator.generate_random()
    name = Patient.name
    logging.debug("Generated name: %s", name)