from django.urls import path
from .views import SubscriptionCreateAPIView,SubscriptionList,PlanList, SubscriptionCancelAPIView

urlpatterns = [
    path('subscriptions/', SubscriptionCreateAPIView.as_view()),
    path('subscriptions/list/', SubscriptionList.as_view()),
    path('plans/', PlanList.as_view()),
    path('subscriptions/<int:subscription_id>/cancel/', SubscriptionCancelAPIView.as_view()),
]   