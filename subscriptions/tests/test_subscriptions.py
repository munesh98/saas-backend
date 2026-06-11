from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from subscriptions.models import Subscription, Plan

User = get_user_model()

class SubscriptionAPITest(TestCase) :
    
    def setUp(self):
        self.client = APIClient()
        self.create_url = '/api/subscriptions/'
        self.cancel_url = '/api/subscriptions/{id}/cancel/'
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_verified=True
        )
        self.plan = Plan.objects.create(
            name='Basic',
            code='BASIC',
            price=199.00,
            duration_days=30,
            description='Basic plan'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_subscription(self):
        data = {
            'plan': self.plan.id
        }
        response = self.client.post(self.create_url, data, format='json')
    
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Subscription.objects.count(), 1)
        self.assertEqual(Subscription.objects.first().status, 'PENDING')
    
    def test_duplicate_active_subscription(self):
        # create active subscription directly
        Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            start_date='2026-01-01',
            end_date='2026-01-31',
            status='ACTIVE'
        )
    
        # try to create another via API
        data = {'plan': self.plan.id}
        response = self.client.post(self.create_url, data, format='json')
    
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Subscription.objects.count(), 1)
    
    def test_cancel_subscription(self):
        # create active subscription
        subscription = Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            start_date='2026-01-01',
            end_date='2026-01-31',
            status='ACTIVE'
        )
    
        # build cancel URL with subscription id
        cancel_url = f'/api/subscriptions/{subscription.id}/cancel/'
    
        response = self.client.patch(cancel_url)
    
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        subscription.refresh_from_db()
        self.assertTrue(subscription.is_cancelled)
    
    
    def test_cancel_other_users_subscription(self):
        # create second user with their own subscription
        second_user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123',
            is_verified=True
        )
        subscription = Subscription.objects.create(
            user=second_user,
            plan=self.plan,
            start_date='2026-01-01',
            end_date='2026-01-31',
            status='ACTIVE'
        )
    
        # self.user tries to cancel second_user's subscription
        # self.client is already authenticated as self.user from setUp
        cancel_url = f'/api/subscriptions/{subscription.id}/cancel/'
        response = self.client.patch(cancel_url)
    
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        subscription.refresh_from_db()
        self.assertFalse(subscription.is_cancelled)    
    
    
    def test_unauthenticated_cannot_create_subscription(self):
        # log out — remove authentication
        self.client.force_authenticate(user=None)
    
        data = {'plan': self.plan.id}
        response = self.client.post(self.create_url, data, format='json')
    
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)   