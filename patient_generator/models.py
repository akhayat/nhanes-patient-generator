import json
from django.db import models

# Create your models here.

class Patient(models.Model):
    first_name = models.TextField()
    last_name = models.TextField()
    age = models.IntegerField()
    sex = models.TextField()
    gender = models.TextField()
    ethnicity = models.TextField(default='')
    primary_language = models.TextField()
    allergies = models.JSONField(default=list, blank=True)
    tobacco_status = models.JSONField(default=dict, blank=True)
    alcohol_use = models.JSONField(default=dict, blank=True)
    drug_use = models.JSONField(default=dict, blank=True)
    housing = models.JSONField(default=list, blank=True)
    employment = models.JSONField(default=list, blank=True)
    education = models.JSONField(default=list, blank=True)
    marital_status = models.JSONField(default=list, blank=True)
    children = models.IntegerField(default=0)
    pets = models.JSONField(default=dict, blank=True)
    travel = models.JSONField(default=dict, blank=True)
    chief_complaint = models.TextField()
    diet = models.JSONField(default=list, blank=True)

    def to_dict(self) -> dict:
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "age": self.age,
            "sex": self.sex,
            "gender": self.gender,
            "ethnicity": self.ethnicity,
            "primary_language": self.primary_language,
            "allergies": self.allergies,
            "tobacco_status": self.tobacco_status,
            "alcohol_use": self.alcohol_use,
            "drug_use": self.drug_use,
            "housing": self.housing,
            "employment": self.employment,
            "education": self.education,
            "marital_status": self.marital_status,
            "children": self.children,
            "pets": self.pets,
            "travel": self.travel,
            "chief_complaint": self.chief_complaint,
            "diet": self.diet,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            age=data.get("age", 0),
            sex=data.get("sex", ""),
            gender=data.get("gender", ""),
            ethnicity=data.get("ethnicity", ""),
            primary_language=data.get("primary_language", ""),
            allergies=data.get("allergies", []),
            tobacco_status=data.get("tobacco_status", {}),
            alcohol_use=data.get("alcohol_use", {}),
            drug_use=data.get("drug_use", {}),
            housing=data.get("housing", []),
            employment=data.get("employment", []),
            education=data.get("education", []),
            marital_status=data.get("marital_status", []),
            children=data.get("children", 0),
            pets=data.get("pets", {"dogs": 0, "cats": 0, "birds": 0, "other": 0}),
            sick_contacts=data.get("sick_contacts", False),
            travel=data.get("travel", {"domestic": False, "international": False}),
            diet=data.get("diet", []),
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4)

    @classmethod
    def from_json(cls, json_str: str):
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    class Gender(models.TextChoices):
        MALE = "Male"
        FEMALE = "Female"
        OTHER = "Other"

    class HousingStatus(models.TextChoices):
        OWNED = "Owned"
        RENTED = "Rented"
        HOMELESS = "Homeless"
        OTHER = "Other"


    class Diet(models.TextChoices):
        OMNIVORE = "Omnivore"
        VEGETARIAN = "Vegetarian"
        VEGAN = "Vegan"
        OTHER = "Other"

    class SubstanceUseFrequency(models.TextChoices):
        NEVER = "Never"
        OCCASIONALLY = "Occasionally"
        REGULARLY = "Regularly"
        DAILY = "Daily"

    class Race(models.TextChoices):
        WHITE = "White"
        BLACK = "Black"
        AAPI = "Asian American and Pacific Islander"
        HISPANIC = "Hispanic"

    class Meta:
        db_prefix = None
        db_table = 'generated_patient'

class AggregatedNhanesData(models.Model):
    field_name = models.TextField()
    value = models.TextField()
    gender = models.CharField(max_length=1, blank=True, null=True)
    race = models.TextField(blank=True, null=True)
    count = models.IntegerField()
    range_of_values = models.BooleanField(blank=True, null=True, default=False)
    mean = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    median = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    mode = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    stdev = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    variance = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    q1 = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    q2 = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    q3 = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    is_int = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_prefix = None
        db_table = 'nhanes_aggregated'

