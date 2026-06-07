from django.urls import path
from .views import RegisterationCreateAPIView,VerifyEmailView, CustomTokenObtainPairView,PasswordResetView,PasswordUpdateView


urlpatterns = [
    path('register/', RegisterationCreateAPIView.as_view()),
    path('verify-email/', VerifyEmailView.as_view()),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('password-reset-email/', PasswordResetView.as_view()),
    path('password-update/', PasswordUpdateView.as_view()),
]