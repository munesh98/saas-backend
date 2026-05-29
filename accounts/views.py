from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer
from rest_framework.permissions import AllowAny

class RegisterationCreateAPIView(APIView):
    permission_classes = [AllowAny]  # override global IsAuthenticated
    
    def post(self, request):
        serializer = RegisterSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            registeration = serializer.save()
            return Response(
                           {"message": "User registered successfully"},
                           status=status.HTTP_201_CREATED
                            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )