from rest_framework.response import Response
from rest_framework import generics, status, permissions , exceptions
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from .serializers import RegisterSerializer
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.shortcuts import render
from bookings.models import Booking
from django.contrib.auth.decorators import login_required
from .decoraters import worker_required
from django.contrib.auth import logout

def index(request):
    user = None
    if request.user.is_authenticated:
        user = request.user
    return render(request, "home.html", {"user": user})

def login_page(request):
    return render(request,"login.html")

def register_page(request):
    return render(request,"register.html")

@worker_required
def worker_profile_create_page(request):
    return render(request,"worker_profile_create.html")

@worker_required
def dashboard_page(request):
    return render(request,"worker_dashboard.html")

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self,request):
        username = request.data.get("username")
        password = request.data.get("password")
        role = request.data.get("role")
        user = authenticate(username=username,password=password)
        if user.role != role:
            return Response({"message":"Please select correct role"},status=403)
        if user:
            refresh = RefreshToken.for_user(user)
            response = Response({"message":"Login Succesfull"},status=200)
            response.set_cookie(
                key = "access_token",
                value = str(refresh.access_token),
                httponly = True,
                samesite = "Lax",
                secure = False # Change while production
            )
            response.set_cookie(
                key="refresh_token",
                value = str(refresh),
                httponly = True,
                samesite = "Lax",
                secure = False
            )
            return response
        return Response({"message":"Invalid Credentials"},status = 401)

# worker profile views
from rest_framework import permissions
from .models import WorkerProfile
from .serializers import WorkerProfileSerializer

class WorkerProfileCreateView(generics.CreateAPIView):
    queryset = WorkerProfile.objects.all()
    serializer_class = WorkerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        
        if self.request.user.role != 'worker':
            raise ValueError("Only workers can create a profile.")
        serializer.save(user=self.request.user)



class WorkerListView(generics.ListAPIView):
    queryset = WorkerProfile.objects.filter(is_available=True)
    serializer_class = WorkerProfileSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        location = self.request.query_params.get('location')
        if category:
            queryset = queryset.filter(category=category)
        if location:
            queryset = queryset.filter(location__icontains=location)
        return queryset


# for worker search
from .serializers import WorkerProfileListSerializer

class WorkerSearchView(generics.ListAPIView):
    serializer_class = WorkerProfileListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = WorkerProfile.objects.filter(is_available=True)
        category = self.request.query_params.get('category')
        location = self.request.query_params.get('location')

        if category:
            queryset = queryset.filter(category=category)
        if location:
            queryset = queryset.filter(location__icontains=location)

        return queryset[:5]

# worker update is_avalibility
class UpdateWorkerAvailabilityView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'worker':
            return Response({'error': 'Only workers can update availability'}, status=403)
        
        try:
            worker_profile = request.user.worker_profile
        except WorkerProfile.DoesNotExist:
            return Response({'error': 'Worker profile not found'}, status=404)

        worker_profile.is_available = request.data.get('is_available', True)
        worker_profile.save()

        return Response({'message': 'Availability updated', 'is_available': worker_profile.is_available})
    
    
# api for worker_profile
class WorkerDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        access_key = request.COOKIES.get("access_token")
        if not access_key:
            return Response({"error": "Access token missing"}, status=401)

        try:
            validate_token = AccessToken(access_key)
            user_id = validate_token["user_id"]
            user = User.objects.get(id=user_id)
        except Exception:
            return Response({"error": "Invalid token"}, status=401)

        if user.role != "worker":
            return Response({"error": "Only workers allowed"}, status=403)

        # Worker profile and bookings
        profile = WorkerProfile.objects.filter(user=user).first()
        bookings = Booking.objects.filter(worker=user)

        return Response({
            "username": user.username,
            "first_name":user.first_name,
            "last_name":user.last_name,
            "email": user.email,
            "profile": {
                "is_available":profile.is_available if profile else None,
                "skill": profile.category if profile else None,
                "experience": profile.experience_years if profile else None,
                "location": profile.location if profile else None,
            },
            "total_bookings": bookings.count(),
            "completed_bookings": bookings.filter(status="completed").count(),
            "pending_bookings": bookings.filter(status="pending").count(),
        })
    
# check user have profile or not
class ProfileCheckView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self,request):
        #check user is exist or not
        has_profile = WorkerProfile.objects.filter(user = request.user).exists()
        return Response({"has_profile":has_profile})
    
# check user loged in or not for searching opration
class AuthCheckView(APIView):
    def get(self, request):
        return Response({"is_authenticated": request.user.is_authenticated})


# Log out API
class LogoutAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Create a response
        response = Response({"success": True, "message": "Logged out successfully"})
        
        # Delete the JWT cookie
        response.delete_cookie('access_token') 
        response.delete_cookie('refresh_token') 

        return response
