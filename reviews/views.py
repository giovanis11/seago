from django.shortcuts import render
from django.http import HttpResponse

def review_create(request, boat_id):
    return HttpResponse(f'Review create form for boat {boat_id} coming soon')
def review_delete(request, pk):
    return HttpResponse(f'Review delete confirmation for review {pk} coming soon')