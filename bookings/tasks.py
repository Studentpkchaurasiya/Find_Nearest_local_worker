# from celery import shared_task
# from django.utils import timezone
# from .models import Booking

# @shared_task
# def monitor_booking(booking_id):
#     """
#     Check booking status every 2 seconds for 1 minute.
#     If worker changes status → stop monitoring.
#     If still pending after 1 min → auto reject.
#     """
#     try:
#         booking = Booking.objects.get(id=booking_id)
#     except Booking.DoesNotExist:
#         return f"Booking {booking_id} not found"

#     total_time = 0
#     interval = 2  # seconds
#     max_time = 60  # 1 minute

#     while total_time < max_time:
#         booking.refresh_from_db()  # get latest status

#         if booking.status != "pending":
#             # Worker already accepted/rejected
#             return f"Booking {booking_id} status updated: {booking.status}"

#         # Wait 2 seconds
#         import time
#         time.sleep(interval)
#         total_time += interval

#     # After 1 min, still pending → auto reject
#     booking.status = "rejected"
#     booking.save()
#     return f"Booking {booking_id} auto-rejected"
