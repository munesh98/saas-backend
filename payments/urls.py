from django.urls import path
from .views import PaymentCreateAPIView,PaymentVerifyAPIView,PaymentList,MeView,RazorpayOrderCreateAPIView,RazorpayWebhookAPIView

urlpatterns = [
    path('payments/', PaymentCreateAPIView.as_view()),
    path('payments/verify/', PaymentVerifyAPIView.as_view()),
    path('payments/list/', PaymentList.as_view()),
    path('me/', MeView.as_view()),
    path('payments/create-order/', RazorpayOrderCreateAPIView.as_view()),
    path('payments/webhook/', RazorpayWebhookAPIView.as_view()),
    
]