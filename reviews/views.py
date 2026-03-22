from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Review
from boats.models import Boat


@login_required
@require_POST
def review_create(request, boat_id):
    boat = get_object_or_404(Boat, pk=boat_id)
    rating = request.POST.get('rating')
    comment = request.POST.get('comment', '').strip()

    if not rating or not rating.isdigit() or not (1 <= int(rating) <= 5):
        return JsonResponse({'error': 'Invalid rating.'}, status=400)

    review, created = Review.objects.update_or_create(
        user=request.user,
        boat=boat,
        defaults={'rating': int(rating), 'comment': comment}
    )

    return JsonResponse({
        'status': 'created' if created else 'updated',
        'rating': review.rating,
        'comment': review.comment,
        'username': request.user.username,
        'average': boat.average_rating(),
    })


@login_required
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk, renter=request.user)
    review.delete()
    return JsonResponse({'status': 'deleted'})