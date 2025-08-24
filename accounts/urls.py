from django.urls import path
from .views import RegisterView, LoginView, WorkerProfileCreateView, WorkerListView, WorkerSearchView,UpdateWorkerAvailabilityView, WorkerDashboardView
from .views import ProfileCheckView, AuthCheckView, LogoutAPIView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('worker/create/', WorkerProfileCreateView.as_view()),
    path('profile/check/',ProfileCheckView.as_view()),
    path('worker/dashboard/', WorkerDashboardView.as_view()),
    path('worker/list/', WorkerListView.as_view(), name='worker-list'),
    path('worker/search/', WorkerSearchView.as_view(), name='worker-search'),
    path('user/status/', AuthCheckView.as_view()),
    path('logout/', LogoutAPIView.as_view()),
    path('worker/availability/', UpdateWorkerAvailabilityView.as_view(), name='update-worker-availability'),
]
