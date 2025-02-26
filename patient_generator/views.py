from django.shortcuts import render
from django.http import JsonResponse
from . import patient_generator

def generate(request):
    return JsonResponse(patient_generator.generate_random_patient_as_json())
