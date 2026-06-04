from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import PaymentSerializer
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from .models import Payment
import uuid
import razorpay
from django.conf import settings
from subscriptions.models import Subscription
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.permissions import AllowAny

razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)


class PaymentCreateAPIView(APIView):

    def post(self, request):
        serializer = PaymentSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            payment = serializer.save()
            return Response(
                PaymentSerializer(payment).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )






class PaymentVerifyAPIView(APIView):

    def post(self, request):
        # Extract data
        payment_id = request.data.get('payment_id')
        payment_status = request.data.get('status')

        # Validate input
        if not payment_id or not payment_status:
            raise ValidationError("payment_id and status are required.")

        if payment_status not in ['SUCCESS', 'FAILED']:
            raise ValidationError("Invalid status value.")

        # Fetch payment
        payment = get_object_or_404(Payment, id=payment_id)

        # Security check
        if payment.user != request.user:
            raise ValidationError("You are not authorized to verify this payment.")

        # Prevent re-processing
        if payment.status != 'PENDING':
            raise ValidationError("Payment already processed.")

        # Update payment
        payment.status = payment_status
        
        if payment.subscription.status == 'ACTIVE':
            raise ValidationError("Subscription is already active. Payment not required.")
        
        if payment_status == 'SUCCESS':
            payment.transaction_id = str(uuid.uuid4())

            # Update subscription
            subscription = payment.subscription
            subscription.status = 'ACTIVE'
            subscription.save()

        else:
            payment.transaction_id = None

        payment.save()

        # Response
        return Response(
            {
                "message": "Payment verified successfully",
                "payment_id": payment.id,
                "status": payment.status
            },
            status=status.HTTP_200_OK
        )


class RazorpayOrderCreateAPIView(APIView):
    def post(self, request):
        # get subscription_id from request
        subscription_id = request.data.get('subscription_id')
        
        # fetch subscription
        subscription = get_object_or_404(Subscription , id = subscription_id)
        if subscription.user != request.user :
            raise ValidationError("You cannot pay to other's subscription")
        if subscription.status != "PENDING" :
            raise ValidationError("You do not have any pending payments")
        
        # create razorpay order
        amount = int(subscription.plan.price * 100)  # convert to paise 
        razorpay_order = razorpay_client.order.create({
            'amount': amount,
            'currency': 'INR',
            'payment_capture': 1  # auto capture payment
            })
        
        # save razorpay order id to payment record
        payment = get_object_or_404(Payment, subscription=subscription, status='PENDING')
        payment.razorpay_order_id = razorpay_order['id']
        payment.save()
        
        # return order details
        return Response({
            'order_id': razorpay_order['id'],
            'amount': amount,
            'currency': 'INR',
            'key_id': settings.RAZORPAY_KEY_ID,
            'subscription_id': subscription.id,
            }, status=status.HTTP_201_CREATED)




@method_decorator(csrf_exempt, name='dispatch')
class RazorpayWebhookAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        # get webhook payload
        webhook_body = request.body
        webhook_signature = request.headers.get('X-Razorpay-Signature')
        
        # verify signature
        try:
            razorpay_client.utility.verify_webhook_signature(
                webhook_body.decode('utf-8'),
                webhook_signature,
                settings.RAZORPAY_KEY_SECRET
            )
        except Exception:
            return Response(
                {"error": "Invalid signature"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # parse payload
        payload = json.loads(webhook_body)
        
        # only handle successful payments
        if payload['event'] != 'payment.captured':
            return Response({"message": "Event ignored"}, status=status.HTTP_200_OK)
        
        # get razorpay order id from payload
        razorpay_order_id = payload['payload']['payment']['entity']['order_id']
        
        # find payment record
        payment = get_object_or_404(Payment, razorpay_order_id=razorpay_order_id)
        
        # prevent reprocessing
        if payment.status != 'PENDING':
            return Response({"message": "Already processed"}, status=status.HTTP_200_OK)
        
        # update payment
        payment.status = 'SUCCESS'
        payment.transaction_id = payload['payload']['payment']['entity']['id']
        payment.save()
        
        # update subscription
        subscription = payment.subscription
        subscription.status = 'ACTIVE'
        subscription.save()
        
        return Response({"message": "Payment processed"}, status=status.HTTP_200_OK)            


class PaymentList(APIView):

    def get(self, request):
        user = request.user
        payments = Payment.objects.filter(user=user)
        
        if not payments:
            return Response({
                            "message": "No payments found",
                            "data": []
                            }, 
                            status=status.HTTP_200_OK)
        
        serializer = PaymentSerializer(payments, many=True)#converting into json format

        return Response({
                        "message": "Payments fetched successfully",
                        "data": serializer.data
                        }
                        , status=status.HTTP_200_OK)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "id": request.user.id,
            "username": request.user.username,
        })