from django.shortcuts import render, get_object_or_404
from .models import Service
from django.db.models import Q
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return render(request, 'home.html')

def service_list(request):
    services = Service.objects.all()
    
    # Search by name or description
    query = request.GET.get('q')
    if query:
        services = services.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    
    # Filter by service type
    service_type = request.GET.get('type')
    if service_type:
        services = services.filter(service_type=service_type)
    
    # Filter by price range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price and max_price:
        try:
            services = services.filter(price__gte=float(min_price), price__lte=float(max_price))
        except ValueError:
            pass
    
    # Sort by rating
    sort_by = request.GET.get('sort')
    if sort_by == 'rating':
        services = sorted(services, key=lambda s: s.average_rating(), reverse=True)
    elif sort_by == 'price_low':
        services = services.order_by('price')
    elif sort_by == 'price_high':
        services = services.order_by('-price')
    
    # Get service types for filter dropdown
    service_types = Service.SERVICE_TYPES
    
    context = {
        'services': services,
        'service_types': service_types,
        'query': query,
        'current_type': service_type,
    }
    return render(request, 'services/service_list.html', context)

def service_detail(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    reviews = service.reviews.all()
    is_wishlisted = False
    
    if request.user.is_authenticated:
        from bookings.models import Wishlist
        is_wishlisted = Wishlist.objects.filter(user=request.user, service=service).exists()
    
    context = {
        'service': service,
        'reviews': reviews,
        'average_rating': service.average_rating(),
        'review_count': service.review_count(),
        'is_wishlisted': is_wishlisted,
    }
    return render(request, 'services/service_detail.html', context)

