from django.shortcuts import render
from django.http import HttpResponse

def homepage(request):
    return HttpResponse('Homepage coming soon')
def boat_list(request):
    return HttpResponse('Boat list coming soon')
def boat_detail(request, boat_id):
    return HttpResponse(f'Boat detail for boats coming soon')
def boat_create(request):
    return HttpResponse('Boat create form coming soon')
def boat_edit(request, boat_id):
    return HttpResponse(f'Boat edit form for boats coming soon')
def boat_delete(request, boat_id):
    return HttpResponse(f'Boat delete confirmation for boats coming soon')
def wishlist(request):
    return HttpResponse('Wishlist coming soon')
