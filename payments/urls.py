from django.urls import path
from .views import PaymentCreateAPIView,PaymentVerifyAPIView,PaymentList

urlpatterns = [
    path('payments/', PaymentCreateAPIView.as_view()),
    path('payments/verify/', PaymentVerifyAPIView.as_view()),
    path('payments/list/', PaymentList.as_view()),
]