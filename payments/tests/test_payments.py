from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from subscriptions.models import Subscription, Plan
from payments.models import Payment

User = get_user_model()

class PaymentAPITest(TestCase) :
    
    def setUp(self):
        self.client = APIClient()
        self.url = '/api/payments/'
        self.success_url = '/api/payments/verify/'
    
        self.user = User.objects.create_user(
            username = "testuser",
            email = "test@example.com",
            password = "testpass123",
            is_verified = True
            )
        
        self.plan = Plan.objects.create(
            name = "Basic",
            code = "BASIC",
            price = 199.00,
            duration_days = 30,
            description = 'Basic plan'
            )
        self.subscription = Subscription.objects.create(
            user = self.user,
            plan = self.plan,
            start_date = '2026-01-01',
            end_date = '2026-01-31',
            status = "PENDING"
        )
        self.client.force_authenticate(user=self.user) 
    
    def test_create_payment(self):
        data = {'subscription': self.subscription.id}
        response = self.client.post(self.url, data, format='json')
    
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(Payment.objects.first().status, 'PENDING')
    
    def test_duplicate_payment(self):
        Payment.objects.create(
            user=self.user,
            subscription=self.subscription,
            amount=199.00,
            status='PENDING'
        )
    
        data = {'subscription': self.subscription.id}
        response = self.client.post(self.url, data, format='json')
    
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Payment.objects.count(), 1)
    
    def test_payment_verify_success(self):
        payment = Payment.objects.create(
            user=self.user,
            subscription=self.subscription,
            amount=199.00,
            status='PENDING'
        )
        
        data = {
            'payment_id' : payment.id,
            'status' : "SUCCESS"
        }
        response = self.client.post(self.success_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Payment.objects.first().status, 'SUCCESS')
        self.assertEqual(Subscription.objects.first().status, 'ACTIVE')
    
    def test_payment_verify_wrong_user(self):
        
        self.second_user = User.objects.create_user(
            username = "testuser2",
            email = "test2@example.com",
            password = "testpass123",
            is_verified = True
            )
        
        payment = Payment.objects.create(
            user=self.user,
            subscription=self.subscription,
            amount=199.00,
            status='PENDING'
        )
        self.client.force_authenticate(user=self.second_user)
        
        data = {
            'payment_id' : payment.id,
            'status' : "SUCCESS"
        }
        response = self.client.post(self.success_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Payment.objects.first().status, "PENDING")
        self.assertEqual(Subscription.objects.first().status, "PENDING")