from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Booking
from .serializers import BookingSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers


class BookingCreateView(generics.CreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role != 'customer':
            raise serializers.ValidationError("Only customers can create bookings.")
        
        # Save booking with logged-in user as customer
        serializer.save(customer=self.request.user)


class WorkerBookingListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(worker=self.request.user)
    
class WorkerPendingRequestsView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        from django.utils import timezone
        one_min_ago = timezone.now() - timezone.timedelta(minutes=1)
        return Booking.objects.filter(
            worker=self.request.user,
            status="pending",
            created_at__gte=one_min_ago
        )


# accept / reject api

class BookingStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        booking = Booking.objects.get(pk=pk, worker=request.user)
        status_value = request.data.get('status')
        if status_value in ['accepted', 'rejected']:
            booking.status = status_value
            booking.save()
            return Response({'message': f'Booking {status_value}.'})
        return Response({'error': 'Invalid status'}, status=400)

# check booking status
from .serializers import BookingStatusSerializer

class BookingStatusView(generics.RetrieveAPIView):
    serializer_class = BookingStatusSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        booking_id = self.kwargs.get('pk')
        return Booking.objects.filter(id=booking_id)
