from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework import status
from .serializers import SubscriptionSerializer, PlanSerializer
from .models import Subscription, Plan
from django.http import HttpResponse
from .tasks import send_subscription_confirmation_email
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema


def home(request):
    return HttpResponse("Backend is live 🚀")


@extend_schema(responses=PlanSerializer(many=True))
class PlanList(APIView):
    permission_classes = [AllowAny]
    
    def get(self,request):
        plans = Plan.objects.all()
        serializer = PlanSerializer(plans, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)



@extend_schema(request=SubscriptionSerializer, responses=SubscriptionSerializer)
class SubscriptionCreateAPIView(APIView):

    def post(self, request):
        serializer = SubscriptionSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            subscription = serializer.save()
            send_subscription_confirmation_email.delay(user_email = request.user.email,
                                                       username = request.user.username,
                                                       plan_name = subscription.plan.name,
                                                       end_date = subscription.end_date,
                                                       )
            return Response(
                SubscriptionSerializer(subscription).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(responses=SubscriptionSerializer(many=True))
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
                        
 


@extend_schema(
    responses={"200": {"description": "Subscription cancelled successfully"}}
)
class SubscriptionCancelAPIView(APIView):

    def patch(self, request, subscription_id):
        subscription = get_object_or_404(Subscription, id=subscription_id)

        if subscription.user != request.user:
            raise ValidationError("You are not authorized to cancel this subscription.")

        if subscription.status != "ACTIVE":
            raise ValidationError("No active subscription found to cancel.")

        subscription.is_cancelled = True
        subscription.auto_renew = False
        subscription.save()

        return Response(
            {"message": "Subscription cancelled successfully. You will have access until your billing period ends."},
            status=status.HTTP_200_OK
        )