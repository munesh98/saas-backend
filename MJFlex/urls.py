from django.contrib import admin
from django.urls import path, include
from subscriptions.views import home
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views import CustomTokenObtainPairView

urlpatterns = [
    path('', home),
    path("admin/", admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/', include('subscriptions.urls')),
    path('api/', include('payments.urls')),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]