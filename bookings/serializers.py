from rest_framework import serializers
from .models import Booking
from accounts.models import WorkerProfile

class BookingSerializer(serializers.ModelSerializer):
    customer_fname = serializers.CharField(source="customer.first_name", read_only=True) 
    customer_lname = serializers.CharField(source="customer.last_name", read_only=True) 
    customer_email = serializers.CharField(source="customer.email", read_only=True)

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['customer', 'status']

    def create(self, validated_data):
        worker = validated_data['worker']

        try:
            worker_profile = WorkerProfile.objects.get(user=worker)
        except WorkerProfile.DoesNotExist:
            raise serializers.ValidationError("Worker profile not found.")

        # Check availability
        if not worker_profile.is_available:
            raise serializers.ValidationError("Worker is not available.")

        # Mark worker unavailable
        worker_profile.is_available = False
        worker_profile.save()

        # Always set booking status as pending
        validated_data['status'] = "pending"

        return super().create(validated_data)

# check bookings status
class BookingStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["id", "status"]