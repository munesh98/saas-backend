from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SubscriptionSerializer
from .models import Subscription
from django.http import HttpResponse


def home(request):
    return HttpResponse("Backend is live 🚀")

class SubscriptionCreateAPIView(APIView):

    def post(self, request):
        serializer = SubscriptionSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            subscription = serializer.save()
            return Response(
                SubscriptionSerializer(subscription).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionList(APIView):

    def get(self, request):
        user = request.user
        subscriptions = Subscription.objects.filter(user=user)

        serializer = SubscriptionSerializer(subscriptions, many=True)

        return Response({
                        "message": "Subscriptions fetched successfully",
                        "data": serializer.data
                        }, 
                        status=status.HTTP_200_OK)