from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PaymentSerializer
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from .models import Payment
import uuid


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
        
        serializer = PaymentSerializer(payments, many=True)

        return Response({
                        "message": "Payments fetched successfully",
                        "data": serializer.data
                        }
                        , status=status.HTTP_200_OK)