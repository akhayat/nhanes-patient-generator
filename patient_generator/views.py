from django.shortcuts import render
from django.http import JsonResponse
from patient_generator import generator
from patient_generator import nhanes_stats
from patient_generator import metainfo
from patient_generator import nhanes_search


def generate(request):
    return JsonResponse(generator.generate_random_patient())

def stats(request):
    return JsonResponse(nhanes_stats.data_for_variable(request.GET['table'], request.GET['variable']), safe=False)

def table_info(request):
    return JsonResponse(metainfo.table_info(), safe=False)

def search(request):
    return JsonResponse(nhanes_search.search(request.GET['q'], request.GET.get('limit', None)), safe=False)
