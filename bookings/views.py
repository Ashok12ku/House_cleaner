from django.shortcuts import render, redirect, get_object_or_404
from .forms import BookingForm, ReviewForm, CancellationForm, WishlistForm
from .models import Booking, Wishlist
from services.models import Service, Review
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import requests
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from django.http import FileResponse
import io
from .utils import send_booking_email
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q

User = get_user_model()
# Create your views here.
def bookings_home(request):
    return redirect('my_bookings')


@login_required(login_url='/accounts/login/')
def create_booking(request, service_id):
    service = Service.objects.get(id=service_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.service = service
            booking.status = 'pending'
            booking.payment_status = 'pending'
            booking.save()

             # 🔹 Cashfree Payment Order Create
            url = "https://sandbox.cashfree.com/pg/orders"
            headers = {
                "x-client-id": settings.CASHFREE_APP_ID,
                "x-client-secret": settings.CASHFREE_SECRET_KEY,
                "x-api-version": "2022-09-01",
                "Content-Type": "application/json"
            }

            data = {
                "order_id": f"order_{booking.id}",
                "order_amount": float(service.price),
                "order_currency": "INR",
                "customer_details": {
                    "customer_id": str(request.user.id),
                    "customer_email": request.user.email,
                    "customer_phone": "9999999999"
                },
                "order_meta": {
                    "return_url": request.build_absolute_uri('/bookings/payment_success/')
                }
            }

            response = requests.post(url, headers=headers, json=data)
            payment_data = response.json()

            return render(request, 'bookings/payment.html', {
                'booking': booking,
                'payment': payment_data,
                'cashfree_key': settings.CASHFREE_APP_ID,
                'amount': service.price,
            })
    else:
        form = BookingForm()

    return render(request, 'bookings/create_booking.html', {'service': service, 'form': form})

@login_required(login_url='/accounts/login/')
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-date')
    return render(request, 'bookings/my_bookings.html', {'bookings': bookings})


@login_required(login_url='/accounts/login/')
def add_review(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user, status='completed')
    
    # Check if review already exists
    if hasattr(booking, 'review'):
        messages.info(request, "You have already reviewed this booking.")
        return redirect('my_bookings')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.service = booking.service
            review.customer = request.user
            review.save()
            
            # Update provider rating
            if booking.service.serviceproviderprofile:
                booking.service.serviceproviderprofile.update_rating()
            
            messages.success(request, "Thank you for your review!")
            return redirect('my_bookings')
    else:
        form = ReviewForm()
    
    return render(request, 'bookings/add_review.html', {'form': form, 'booking': booking})


@login_required(login_url='/accounts/login/')
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if not booking.can_cancel():
        messages.error(request, "This booking cannot be cancelled. Minimum 24 hours notice required.")
        return redirect('my_bookings')
    
    if request.method == 'POST':
        form = CancellationForm(request.POST)
        if form.is_valid():
            from django.utils import timezone
            booking.status = 'cancelled'
            booking.cancelled_at = timezone.now()
            booking.cancellation_reason = form.cleaned_data.get('reason', '')
            booking.save()
            
            # Send cancellation email
            send_booking_email(request.user, booking, email_type='cancellation')
            
            messages.success(request, "Booking cancelled successfully. Refund will be processed within 5-7 days.")
            return redirect('my_bookings')
    else:
        form = CancellationForm()
    
    return render(request, 'bookings/cancel_booking.html', {'form': form, 'booking': booking})


@login_required(login_url='/accounts/login/')
def toggle_wishlist(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, service=service)
    
    if not created:
        wishlist_item.delete()
        messages.info(request, "Removed from favorites.")
    else:
        messages.success(request, "Added to favorites!")
    
    return redirect(request.META.get('HTTP_REFERER', 'service_list'))



@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        data = request.POST or request.GET

        order_id = data.get('order_id')
        payment_status = data.get('payment_status')

        if payment_status == "SUCCESS":
            booking = Booking.objects.filter(id=order_id.split('_')[-1]).first()
            if booking:
                booking.payment_status = 'paid'
                booking.status = 'confirmed'
                booking.save()

                send_booking_email(booking.user, booking)
                return redirect('download_invoice')
        else:
            return HttpResponse("❌ Payment Failed or Cancelled!")

    return HttpResponse("Invalid Request")

@login_required(login_url='/accounts/login/')
def download_invoice(request):
    booking = Booking.objects.filter(user=request.user).last()  # Latest booking

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    p.setFont("Helvetica-Bold", 18)
    p.drawString(200, 800, "House Cleaner Invoice 🧾")

    p.setFont("Helvetica", 12)
    p.drawString(100, 760, f"Customer Name: {booking.user.username}")
    p.drawString(100, 740, f"Service: {booking.service.name}")
    p.drawString(100, 720, f"Price: ₹{booking.service.price}")
    p.drawString(100, 700, f"Booking Date: {booking.date}")
    p.drawString(100, 680, f"Booking Time: {booking.time}")
    p.drawString(100, 660, f"Payment Status: {booking.payment_status}")

    p.setFont("Helvetica-Oblique", 10)
    p.drawString(100, 620, "Thank you for choosing House Cleaner! 😊")

    p.showPage()
    p.save()
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename="invoice.pdf")

    # Send booking confirmation email
@login_required(login_url='/accounts/login/')
def book_service(request, service_id):
    service = Service.objects.get(id=service_id)

    if request.method == "POST":
        booking_date = request.POST.get('booking_date')
        booking = Booking.objects.create(user=request.user, service=service, booking_date=booking_date)
        
        # ✅ Email Send
        send_booking_email(request.user, booking)

        return redirect('payment_page', booking_id=booking.id)

    return render(request, 'bookings/book_service.html', {'service': service})  

@staff_member_required  # सिर्फ admin users के लिए
def admin_dashboard(request):
    total_users = User.objects.count()
    total_bookings = Booking.objects.count()
    total_revenue = Booking.objects.filter(payment_status='Paid').aggregate(total=Sum('service__price'))['total'] or 0

    # दिनवार बुकिंग काउंट
    daily_bookings = Booking.objects.values('date').annotate(count=Count('id')).order_by('date')

    context = {
        'total_users': total_users,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'daily_bookings': daily_bookings,
    }
    return render(request, 'admin_dashboard.html', context)

def search_services(request):
    query = request.GET.get('q')
    category = request.GET.get('category')
    price_min = request.GET.get('min')
    price_max = request.GET.get('max')

    services = Service.objects.all()

    if query:
        services = services.filter(Q(name__icontains=query) | Q(description__icontains=query))

    if category:
        services = services.filter(service_type__icontains=category)

    if price_min and price_max:
        services = services.filter(price__gte=price_min, price__lte=price_max)

    context = {'services': services, 'query': query}
    return render(request, 'bookings/search_results.html', context)

@staff_member_required
def manage_bookings(request):
    bookings = Booking.objects.all().order_by('-id')

    if request.GET.get('status'):
        bookings = bookings.filter(status=request.GET.get('status'))

    if request.GET.get('date'):
        bookings = bookings.filter(date=request.GET.get('date'))

    return render(request, 'admin_manage_bookings.html', {'bookings': bookings})
