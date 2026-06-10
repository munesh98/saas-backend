from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from unittest.mock import patch

User = get_user_model()

class RegisterAPITest(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.url = '/api/register/'
    
    @patch('accounts.views.send_verification_email.delay')
    def test_successful_registration(self, mock_task):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'testpass123'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().username, 'testuser')

    @patch('accounts.views.send_verification_email.delay')
    def test_passwords_do_not_match(self, mock_task):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'passtest123'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    @patch('accounts.views.send_verification_email.delay')
    def test_duplicate_username(self, mock_task):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'testpass123'
        }
        self.client.post(self.url, data, format='json')
        
        data_twice = {
            'username': 'testuser',
            'email': 'test2@example.com',
            'password': 'testpass123',
            'password2': 'testpass123'
        }
        response = self.client.post(self.url, data_twice, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)

    @patch('accounts.views.send_verification_email.delay')
    def test_duplicate_email(self, mock_task):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'testpass123'
        }
        self.client.post(self.url, data, format='json')
        
        data_twice = {
            'username': 'test2user',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'testpass123'
        }
        response = self.client.post(self.url, data_twice, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)

    @patch('accounts.views.send_verification_email.delay')
    def test_missing_required_field(self, mock_task):
        data = {
            'username': 'testuser',
            'email': 'testuser@gmail.com',
            'password': 'testpass123',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)