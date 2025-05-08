import logging
import random
import numpy as np
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
        self.patient.gender = self.patient.sex = random.choice(['M', 'F'])
        self.patient.ethnicity = self.generate_race()
        self.patient.first_name, self.patient.last_name = self.generate_name()

    def nhanes_random_value(self, field):
        pool = AggregatedNhanesData.objects.filter(field_name=field)
        size, random_row = len(pool), None
        if size == 0:
            raise ValueError(f"No options found for field: {field}")
        elif size == 1:
            random_row = pool[0]
        else:
            weighted_index_list = []
            for i in range(size):
                weighted_index_list += [i] * pool[i].count
                random_row = pool[random.choice(weighted_index_list)]
        if random_row.range_of_values:
            return np.random.normal(random_row.mean, random_row.stdev)
        else:
            return random_row.value

    def generate_gender(self):
        return random.choice(['M', 'F'])

    def generate_race(self):
        return self.nhanes_random_value('race')

    def generate_name(self):
        with db_tool.cursor() as cursor:
            ethnicity = self.patient.ethnicity if 'other' not in self.patient.ethnicity.lower() else '%'
            cursor.execute(db_tool.query('random_name'), [ethnicity, self.patient.gender])
            result = cursor.fetchone()
            return result

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    patient = PatientGenerator.generate_random()
    name = Patient.name
    logging.debug("Generated name: %s", name)