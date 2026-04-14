from rest_framework import serializers 
from rest_framework.exceptions import ValidationError
from .models import Plan
from .models import Subscription 
from datetime import date, timedelta

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = ['user', 'start_date', 'end_date', 'status']
    
    def create(self, validated_data):
        user = self.context['request'].user
        plan = validated_data['plan']
        start_date = date.today()
        end_date = start_date + timedelta(days=plan.duration_days)
        
        if Subscription.objects.filter(user=user, status='ACTIVE').exists():
            raise ValidationError("User already has an active subscription.")
        
        subscription = Subscription.objects.create(
            user=user,
            plan=plan,
            start_date=start_date,
            end_date=end_date,
            status='ACTIVE',
            auto_renew=False
        )

        return subscription