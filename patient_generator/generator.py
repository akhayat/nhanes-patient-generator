import logging
import random
import numpy as np
from django.db.models import Q
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
        self.patient.age = self.generate_age()
        self.patient.primary_language = self.generate_primary_language()
        self.patient.education = self.generate_education()
        self.patient.children = self.generate_children()
        self.patient.marital_status = self.generate_marital_status()

    def nhanes_random_value(self, field, ethnicity=None):
        query = Q(field_name=field)
        if (ethnicity is not None):
            query = query & (Q(race=ethnicity) if ethnicity != '' else Q(race__isnull=True))
        pool = AggregatedNhanesData.objects.filter(query)
        # logging.debug(f"Query = {pool.query}")
        size, random_row = len(pool), None
        if size == 0:
            raise ValueError(f"No options found for field: {field}")
        else:
            random_row = pool[0] if size == 1 else random_weighted_choice(pool, size)

        if random_row.range_of_values:
            return random_from_normal_dist(random_row.mean, random_row.stdev, random_row.is_int)
        else:
            return random_row.value

    def generate_gender(self):
        return random.choice(['M', 'F'])

    def generate_race(self):
        return self.nhanes_random_value('race')
    
    def generate_primary_language(self):
        return self.nhanes_random_value('primary_language', ethnicity=self.patient.ethnicity if 'hispanic' == self.patient.ethnicity.lower() else '')

    def generate_name(self):
        with db_tool.cursor() as cursor:
            ethnicity = self.patient.ethnicity if 'other' not in self.patient.ethnicity.lower() else '%'
            cursor.execute(db_tool.query('random_name'), [ethnicity, self.patient.gender])
            result = cursor.fetchone()
            return result
        
    def generate_age(self):
        return self.nhanes_random_value('age')
    
    def generate_education(self):
        return self.nhanes_random_value('education')
    
    def generate_children(self):
        return self.nhanes_random_value('children')
    
    def generate_marital_status(self):
        return self.nhanes_random_value('marital_status')
    

    
def random_weighted_choice(pool, size):
    weighted_index_list = []
    for i in range(size):
        weighted_index_list += [i] * pool[i].count
    return pool[random.choice(weighted_index_list)]

def random_from_normal_dist(mean, stdev, is_int):
    rand = np.random.normal(mean, stdev)
    return round(rand) if is_int else rand


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    patient = PatientGenerator.generate_random()
    name = Patient.name
    logging.debug("Generated name: %s", name)