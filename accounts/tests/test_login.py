from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginAPITest(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.url = '/api/token/'
        # create a verified user for testing
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_verified=True
        )
    
    def test_successful_login(self):
        data = {
        'username': 'testuser',
        'password': 'testpass123'
        }
        response = self.client.post(self.url, data, format='json')
    
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_unverified_user_cannot_login(self):
        
        unverified_user = User.objects.create_user(
        username= 'unverified_user',
        email = 'unverifiedemail@gmail.com',
        password = 'unverified@123',
        is_verified = False
        )
        
        data = {
        'username': 'unverified_user',
        'password': 'testpass123'
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_wrong_password(self):
        data = {
        'username': 'testuser',
        'password': 'wrongpassword'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_nonexistent_user(self):
        data = {
        'username': 'nobody',
        'password': 'testpass123'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)