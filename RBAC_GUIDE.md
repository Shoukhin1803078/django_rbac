# Django REST Framework (DRF) দিয়ে রোল-বেসড অ্যাক্সেস কন্ট্রোল (RBAC) গাইড

এই গাইডে আমরা Django REST Framework এবং SimpleJWT ব্যবহার করে একটি সম্পূর্ণ **Role-Based Access Control (RBAC)** বা রোল-বেসড অথরাইজেশন সিস্টেম তৈরির পুরো কোড এবং কাজের ধাপগুলো ধাপে ধাপে আলোচনা করব।

---

## সূচিপত্র (Table of Contents)
1. [প্রজেক্ট কনফিগারেশন (`backend/settings.py`)](#১-প্রজেক্ট-কনফিগারেশন-backendsettingspy)
2. [কাস্টম ইউজার মডেল (`accounts/models.py`)](#২-কাস্টম-ইউজার-مডেল-accountsmodelspy)
3. [কাস্টম পারমিশন ক্লাস (`accounts/permissions.py`)](#৩-কাস্টম-পারমিশন-ক্লাস-accountspermissionspy)
4. [ইউজার রেজিস্ট্রেশন সিরিয়ালাইজার (`accounts/serializers.py`)](#৪-ইউজার-রেজিস্ট্রেশন-সিরিয়ালাইজার-accountsserializerspy)
5. [ভিউসমূহ (`accounts/views.py`)](#৫-ভিউসমূহ-accountsviewspy)
6. [ইউআরএল রাউটিং (`accounts/urls.py` & `backend/urls.py`)](#৬-ইউআরএল-রাউটিং-accountsurlspy--backendurlspy)
7. [পোস্টম্যান (Postman) দিয়ে ধাপে ধাপে টেস্টিং গাইড](#৭-পোস্টম্যান-postman-দিয়ে-ধাপে-ধাপে-টেস্টিং-গাইড)

---

### ১. প্রজেক্ট কনফিগারেশন (`backend/settings.py`)

প্রথমে আমাদের Django প্রজেক্টে `rest_framework`, `accounts` (আমাদের তৈরি অ্যাপ), এবং `rest_framework_simplejwt` যুক্ত করতে হবে। এছাড়া কাস্টম ইউজার মডেল এবং ডিফল্ট অথেনটিকেশন ক্লাস সেট করতে হবে।

```python
# backend/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # থার্ড-পার্টি এবং কাস্টম অ্যাপস
    'rest_framework',
    'accounts',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist', # টোকেন ব্ল্যাকলিস্ট করার জন্য (Logout)
]

# Django REST Framework-এর জন্য ডিফল্ট অথেনটিকেশন হিসেবে JWT সেট করা
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    )
}

# আমাদের কাস্টম ইউজার মডেলটি Django-কে চিনিয়ে দেওয়া
AUTH_USER_MODEL = "accounts.User"
```

---

### ২. কাস্টম ইউজার মডেল (`accounts/models.py`)

আমরা Django-র বিল্ট-ইন ইউজার মডেলকে কাস্টমাইজ করে `AbstractUser` ব্যবহার করেছি। এখানে লগইন করার জন্য ইউজারনেমের পরিবর্তে `email` ব্যবহার করা হচ্ছে এবং প্রতিটি ইউজারের জন্য একটি নির্দিষ্ট `role` (যেমন: admin, user, student) নির্ধারণ করা হয়েছে।

```python
# accounts/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("user", "User"),
        ("student", "Student"),
    )
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")

    # লগইন করার জন্য ইমেইল ব্যবহার করা হবে
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email
```

---

### ৩. কাস্টম পারমিশন ক্লাস (`accounts/permissions.py`)

এটি আমাদের RBAC সিস্টেমের মূল অংশ। এখানে আমরা Django REST Framework-এর `BasePermission` ক্লাস ব্যবহার করে প্রতিটি রোলের জন্য আলাদা পারমিশন ক্লাস তৈরি করেছি।

```python
# accounts/permissions.py

from rest_framework.permissions import BasePermission

class IsAdminRole(BasePermission):
    """
    শুধুমাত্র 'admin' রোলধারী ইউজারদের অ্যাক্সেস অনুমতি দেবে।
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == "admin"
        )

class IsUserRole(BasePermission):
    """
    শুধুমাত্র 'user' রোলধারী ইউজারদের অ্যাক্সেস অনুমতি দেবে।
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == "user"
        )

class IsStudentRole(BasePermission):
    """
    শুধুমাত্র 'student' রোলধারী ইউজারদের অ্যাক্সেস অনুমতি দেবে।
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == "student"
        )
```

---

### ৪. ইউজার রেজিস্ট্রেশন সিরিয়ালাইজার (`accounts/serializers.py`)

নতুন ইউজার রেজিস্ট্রেশন (Sign Up) করার সময় ডাটা ভ্যালিডেশন এবং ডাটাবেজে ইউজার সেভ করার জন্য এই সিরিয়ালাইজারটি ব্যবহার করা হয়।

```python
# accounts/serializers.py

from rest_framework import serializers
from .models import User

class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "username", "password", "role"]

    def create(self, validated_data):
        # create_user মেথডটি পাসওয়ার্ড হ্যাশ (Hash) করে ডাটাবেজে সেভ করে
        user = User.objects.create_user(**validated_data)
        return user
```

---

### ৫. ভিউসমূহ (`accounts/views.py`)

এখানে রেজিস্ট্রেশন, লগআউট এবং আমাদের ৩টি ভিন্ন ড্যাশবোর্ড ভিউ রয়েছে। ড্যাশবোর্ড ভিউগুলোতে আমরা আমাদের তৈরি করা কাস্টম পারমিশন ক্লাসগুলো যুক্ত করেছি।

```python
# accounts/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.http import JsonResponse
from .serializers import SignUpSerializer
from .permissions import IsAdminRole, IsUserRole, IsStudentRole

# ১. সাধারণ হ্যালো ওয়ার্ল্ড ভিউ (টেস্টিংয়ের জন্য)
def hello_world(request):
    return JsonResponse({"message": "Hello World"}, status=status.HTTP_200_OK)

# ২. ইউজার রেজিস্ট্রেশন ভিউ
class SignUpView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User created successfully"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ৩. লগআউট ভিউ (টোকেন ব্ল্যাকলিস্ট করার জন্য)
class LogoutView(APIView):
    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response(
                {"message": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh)
            token.blacklist()
        except TokenError:
            return Response(
                {"message": "Invalid or expired refresh token"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)

# ৪. অ্যাডমিন ড্যাশবোর্ড ভিউ (শুধুমাত্র Admin দেখতে পারবে)
class AdminDashboardView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        return Response({
            "message": "Welcome to the Admin Dashboard!",
            "user": request.user.email,
            "role": request.user.role
        }, status=status.HTTP_200_OK)

# ৫. সাধারণ ইউজার ড্যাশবোর্ড ভিউ (শুধুমাত্র User দেখতে পারবে)
class UserDashboardView(APIView):
    permission_classes = [IsUserRole]

    def get(self, request):
        return Response({
            "message": "Welcome to the User Dashboard!",
            "user": request.user.email,
            "role": request.user.role
        }, status=status.HTTP_200_OK)

# ৬. স্টুডেন্ট ড্যাশবোর্ড ভিউ (শুধুমাত্র Student দেখতে পারবে)
class StudentDashboardView(APIView):
    permission_classes = [IsStudentRole]

    def get(self, request):
        return Response({
            "message": "Welcome to the Student Dashboard!",
            "user": request.user.email,
            "role": request.user.role
        }, status=status.HTTP_200_OK)
```

---

### ৬. ইউআরএল রাউটিং (`accounts/urls.py` & `backend/urls.py`)

#### ক) অ্যাপ লেভেল ইউআরএল (`accounts/urls.py`):
এখানে আমরা সাইনআপ, লগইন, টোকেন রিফ্রেশ, লগআউট এবং ড্যাশবোর্ডের এন্ডপয়েন্টগুলো ডিফাইন করেছি।

```python
# accounts/urls.py

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
    
    # SimpleJWT বিল্ট-ইন ভিউসমূহ
    path('login/', TokenObtainPairView.as_view(), name='login'), # লগইন করে Access ও Refresh টোকেন নেওয়ার জন্য
    path('refresh/', TokenRefreshView.as_view(), name='refresh'), # নতুন Access টোকেন জেনারেট করার জন্য
    
    # ড্যাশবোর্ড এন্ডপয়েন্টসমূহ
    path('dashboard/admin/', AdminDashboardView.as_view(), name='dashboard_admin'),
    path('dashboard/user/', UserDashboardView.as_view(), name='dashboard_user'),
    path('dashboard/student/', StudentDashboardView.as_view(), name='dashboard_student'),
]
```

#### খ) প্রজেক্ট লেভেল ইউআরএল (`backend/urls.py`):
এখানে আমরা `accounts` অ্যাপের ইউআরএলগুলোকে প্রজেক্টের সাথে যুক্ত করেছি।

```python
# backend/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')), # accounts অ্যাপের ইউআরএল যুক্ত করা
]
```

---

### ৭. পোস্টম্যান (Postman) দিয়ে ধাপে ধাপে টেস্টিং গাইড

সার্ভার রান করার পর (`python manage.py runserver`), নিচের ধাপগুলো অনুসরণ করে পোস্টম্যানে টেস্ট করুন:

#### ধাপ ১: রেজিস্ট্রেশন (Sign Up)
* **URL:** `http://127.0.0.1:8000/api/accounts/signup/`
* **Method:** `POST`
* **Body (JSON):**
  ```json
  {
      "email": "alamin@example.com",
      "username": "alamin",
      "password": "Test@123",
      "role": "student"
  }
  ```

#### ধাপ ২: লগইন এবং টোকেন সংগ্রহ (Login)
* **URL:** `http://127.0.0.1:8000/api/accounts/login/`
* **Method:** `POST`
* **Body (JSON):**
  ```json
  {
      "email": "alamin@example.com",
      "password": "Test@123"
  }
  ```
> 💡 রেসপন্স থেকে `access` টোকেনটি কপি করে নিন।

#### 3. ড্যাশবোর্ড অ্যাক্সেস টেস্ট (Testing Authorization)
* **URL:** `http://127.0.0.1:8000/api/accounts/dashboard/student/`
* **Method:** `GET`
* **Authorization Tab:** 
  * Select **Type**: `Bearer Token`
  * Paste your **Access Token** in the token field.
* **ফলাফল:** আপনি সফলভাবে `200 OK` রেসপন্স পাবেন। কিন্তু আপনি যদি এই টোকেন দিয়ে `/dashboard/admin/` এন্ডপয়েন্টে রিকোয়েস্ট পাঠান, তবে **`403 Forbidden`** এরর পাবেন।

---
**অভিনন্দন!** আপনি সফলভাবে Django REST Framework-এ একটি সম্পূর্ণ রোল-বেসড অ্যাক্সেস কন্ট্রোল (RBAC) সিস্টেম তৈরি করে ফেলেছেন।
