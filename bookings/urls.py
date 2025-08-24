from django.urls import path
from .views import BookingCreateView, WorkerBookingListView, BookingStatusUpdateView, WorkerPendingRequestsView, BookingStatusView

urlpatterns = [
    path('create/', BookingCreateView.as_view(), name='booking-create'),
    path('worker/', WorkerBookingListView.as_view(), name='worker-bookings'),
    path('<int:pk>/status/', BookingStatusUpdateView.as_view(), name='booking-status'),
    path("<int:pk>/status/check/", BookingStatusView.as_view(), name="booking-status"),
    path('worker/pending/', WorkerPendingRequestsView.as_view()),
]
