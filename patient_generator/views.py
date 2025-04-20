from django.shortcuts import render
from django.http import JsonResponse
from patient_generator.db_scripts import nhanes_random_respondent
from patient_generator.db_scripts import nhanes_stats
from patient_generator.db_scripts import table_info
from patient_generator.db_scripts import nhanes_search


def generate(request):
    return JsonResponse(nhanes_random_respondent.generate_random_patient())

def stats(request):
    return JsonResponse(nhanes_stats.NHANESStats(
            request.GET['table'], 
            request.GET['variable'], 
            request.GET.get('adultsOnly', False), 
            request.GET.get('gender', None)).data, 
            safe=False)

def tables(request):
    return JsonResponse(table_info.table_info(), safe=False)

def search(request):
    return JsonResponse(nhanes_search.search(
            request.GET['q'], 
            request.GET.get('limit', None)), 
            safe=False)
