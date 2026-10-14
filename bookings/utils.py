from django.core.mail import send_mail
from django.conf import settings

def send_booking_email(user, booking):
    subject = "Your House Cleaning Booking Confirmation 🧹"
    message = f"""
    Hi {user.username},

    Thank you for booking with House Cleaner! 🏡

    Here are your booking details:
    -----------------------------------
    Service: {booking.service.name}
    Date: {booking.booking_date}
    Price: ₹{booking.service.price}
    Status: {booking.status}
    -----------------------------------

    You can download your invoice anytime:
    http://127.0.0.1:8000/bookings/invoice/

    Regards,  
    Team House Cleaner
    """

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
