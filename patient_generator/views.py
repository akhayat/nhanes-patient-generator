from django.shortcuts import render
from django.http import JsonResponse
from . import patient_generator
from . import nhanes_stats
from . import metainfo

def generate(request):
    return JsonResponse(patient_generator.generate_random_patient())

def stats(request):
    return JsonResponse(nhanes_stats.data_for_variable(request.GET['table'], request.GET['variable']), safe=False)

def table_info(request):
    return JsonResponse(metainfo.table_info(), safe=False)
