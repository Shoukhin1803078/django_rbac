from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    SignUpView, 
    LogoutView, 
    hello_world,
    AdminDashboardView,
    UserDashboardView,
    StudentDashboardView
)

urlpatterns = [
    path('hello-world/', hello_world, name='hello_world'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('login/', TokenObtainPairView.as_view(), name='login'), # give two tokens access and refresh
    path('refresh/', TokenRefreshView.as_view(), name='refresh'), # give new access token
    path('dashboard/admin/', AdminDashboardView.as_view(), name='dashboard_admin'),
    path('dashboard/user/', UserDashboardView.as_view(), name='dashboard_user'),
    path('dashboard/student/', StudentDashboardView.as_view(), name='dashboard_student'),
]