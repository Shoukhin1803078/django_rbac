from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .serializers import SignUpSerializer
from django.http import JsonResponse



# # @api_view(["GET"])
# def hello_world(request):
#     # return Response({"message": "Hello World"}, status=status.HTTP_200_OK)



def hello_world(request):
    return JsonResponse({"message": "Hello World"}, status=status.HTTP_200_OK)



class SignUpView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(
                {"message": "User created successfully"},
                status=status.HTTP_201_CREATED
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class LogoutView(APIView):
    def post(self, request):
        # old way
        # refresh_token = request.data.get("refresh_token")
        # token = RefreshToken(refresh_token)
        # token.blacklist()
        refresh = request.data.get("refresh")
        if not refresh:
            return Response(
                {"message": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh)
            token.blacklist()
        except TokenError:
            return Response(
                {"message": "Invalid or expired refresh token"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)