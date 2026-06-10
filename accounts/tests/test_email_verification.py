from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from accounts.models import EmailAccountPasswordVerification

User = get_user_model()

class EmailAPITest(TestCase) :
    
    def setUp(self) :
        self.client = APIClient()
        self.url = '/api/verify-email/'
        
        self.user = User.objects.create_user(
        username = 'testuser',
        email = 'testuser@gmail.com',
        password = 'testuser123',
        is_verified = False 
        )
        
        self.token_record = EmailAccountPasswordVerification.objects.create(
        user=self.user,
        expires_at=timezone.now() + timedelta(hours=24),
        token_type='EMAIL_VERIFICATION'
        )
        
    
    def test_successful_verification(self):
        
        token = str(self.token_record.token).replace('-', '')
        response = self.client.get(f'{self.url}?token={token}')
    
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified)