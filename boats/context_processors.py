from .models import Boat

def locations(request):
    locations = Boat.objects.filter(
        is_approved=True,
        is_available=True
    ).values_list('location', flat=True).distinct()
    return {'all_locations': locations}