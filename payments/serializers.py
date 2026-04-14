from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['user', 'amount', 'status', 'transaction_id', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        subscription = validated_data['subscription']

        # 🔐 Security check
        if user != subscription.user:
            raise ValidationError("You cannot pay for another user's subscription.")

        # ⚠️ Optional but recommended check
        if subscription.status != 'ACTIVE':
            raise ValidationError("Cannot make payment for inactive subscription.")

        amount = subscription.plan.price
        
        if Payment.objects.filter(subscription=subscription,status='PENDING').exists() :
            raise ValidationError("A pending payment already exists for this subscription.")
        
        payment = Payment.objects.create(
            user=user,
            subscription=subscription,
            amount=amount,
            status='PENDING',
            transaction_id=None
        )

        return payment