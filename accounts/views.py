from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer
from rest_framework.permissions import AllowAny
from django.utils import timezone
from datetime import timedelta
from .models import EmailAccountPasswordVerification
from .tasks import send_verification_email, send_password_reset_email
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

class RegisterationCreateAPIView(APIView):
    permission_classes = [AllowAny]  # override global IsAuthenticated
    
    def post(self, request):
        serializer = RegisterSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            registration = serializer.save()

            token_record = EmailAccountPasswordVerification.objects.create(
            user=registration,
            expires_at=timezone.now() + timedelta(hours=24),
            token_type='EMAIL_VERIFICATION')

            send_verification_email.delay(
            email=registration.email,
            username=registration.username,
            token=str(token_record.token).replace('-', '')  # remove dashes
            )
            
            return Response(
                           {"message": "User registered successfully"},
                           status=status.HTTP_201_CREATED
                            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]  # override global IsAuthenticated
    
    def get(self,request):
        token = request.query_params.get('token')
        
        # reformat to UUID with dashes
        formatted_token = f'{token[:8]}-{token[8:12]}-{token[12:16]}-{token[16:20]}-{token[20:]}'
        token_record = get_object_or_404(EmailAccountPasswordVerification, token=formatted_token)
        
        
        if token_record.is_used :
            raise ValidationError("Already verified")
        
        if timezone.now() > token_record.expires_at :
            raise ValidationError("The token is invalid")
            
        token_record.user.is_verified = True
        token_record.user.save()  # save the user
        token_record.is_used = True
        token_record.save()  # save the token record

        return Response(
            {"message": "Email verified successfully. You can now login."},
            status=status.HTTP_200_OK)


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        # get the user
        user = authenticate(
            username=request.data.get('username'),
            password=request.data.get('password')
        )
        
        if user and not user.is_verified:
            return Response(
                {"error": "Please verify your email before logging in."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return response


class PasswordResetView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        
        try:
            User = get_user_model()
            user_record = User.objects.get(email=email)
            token_record = EmailAccountPasswordVerification.objects.create(
                user=user_record,
                expires_at=timezone.now() + timedelta(hours=24),
                token_type='PASSWORD_RESET'
            )
            send_password_reset_email.delay(
                email=email,
                username=user_record.username,
                token=str(token_record.token).replace('-', '')
            )
        except Exception:
            pass
        
        return Response(
            {"message": "If this email is registered you will receive a reset link shortly."},
            status=status.HTTP_200_OK
        )

class PasswordUpdateView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
                
        # reformat to UUID with dashes
        formatted_token = f'{token[:8]}-{token[8:12]}-{token[12:16]}-{token[16:20]}-{token[20:]}'
        token_record = get_object_or_404(EmailAccountPasswordVerification, token=formatted_token ,token_type='PASSWORD_RESET')
        
        if token_record.is_used :
            raise ValidationError("Already verified")
        
        if timezone.now() > token_record.expires_at :
            raise ValidationError("The token is invalid")
        
        if new_password != confirm_password :
            raise ValidationError("Password does not match")
        
        token_record.user.set_password(new_password)
        token_record.user.save()  # save the user
        token_record.is_used = True
        token_record.save()  # save the token
        
        return Response( 
                {"message":"Password reset is successfull"},
                status = status.HTTP_200_OK )
        
        