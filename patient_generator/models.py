import json
from django.db import models

# Create your models here.

class Patient(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()
    sex = models.CharField(max_length=10)
    gender = models.CharField(max_length=10)
    primary_language = models.CharField(max_length=50)
    secondary_language = models.CharField(max_length=50, null=True, blank=True)
    primary_care_physician = models.CharField(max_length=100, null=True, blank=True)
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
    sick_contacts = models.BooleanField(default=False)
    travel = models.JSONField(default=dict, blank=True)
    chief_complaint = models.TextField(null=True, blank=True)
    diet = models.JSONField(default=list, blank=True)

    def to_dict(self) -> dict:
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "age": self.age,
            "sex": self.sex,
            "gender": self.gender,
            "primary_language": self.primary_language,
            "secondary_language": self.secondary_language,
            "primary_care_physician": self.primary_care_physician,
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
            "sick_contacts": self.sick_contacts,
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
            primary_language=data.get("primary_language", ""),
            secondary_language=data.get("secondary_language"),
            primary_care_physician=data.get("primary_care_physician"),
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
            chief_complaint=data.get("chief_complaint"),
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