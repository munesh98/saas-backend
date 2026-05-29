from django.urls import path
from .views import RegisterationCreateAPIView

urlpatterns = [
    path('register/', RegisterationCreateAPIView.as_view()),
]