from django.urls import path
from .views import SubscriptionCreateAPIView,SubscriptionList

urlpatterns = [
    path('subscriptions/', SubscriptionCreateAPIView.as_view()),
    path('subscriptions/list/', SubscriptionList.as_view()),
]