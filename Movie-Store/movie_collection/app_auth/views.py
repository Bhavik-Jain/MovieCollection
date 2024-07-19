from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from .middleware import RequestCounterMiddleware
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .serializers import UserSerializer
from configurations.utils import success_response, error_response
from configurations.message import *

User = get_user_model()


class UserRegistrationView(APIView):
    """
        Description: API for user registration 
        POST /register/
        Payload: {"username": "str", "name": "str", "password": "str"}
        Response: 
                201: Registration successful
                400: Validation errors
                500: Server error
    """
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return success_response(data=serializer.data, message=REGISTRATION_SUCCESS, status=status.HTTP_201_CREATED)
            return error_response(message=str(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            print('error at login -->', error)
            return error_response(message=str(error), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserLoginView(APIView):
    """
        Description: API for user login
        GET /login/
        Payload: {"username": "str", "password": "str"}
        Responses:
                200: Login successful
                401: Invalid credentials
                500: Server error
    """
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            serializer = TokenObtainPairSerializer(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
                print(serializer.validated_data)
                tokens = serializer.validated_data
                access_token = tokens.get('access') if isinstance(tokens, dict) else None
                return success_response(data={'access_token': access_token}, message=LOGIN_SUCCESS, status=status.HTTP_200_OK)
            except TokenError as e:
                raise InvalidToken(e.args[0])
        except InvalidToken:
            return error_response(message="Invalid credentials", status=status.HTTP_401_UNAUTHORIZED)
        except Exception as error:
            print('error at login -->', error)
            return error_response(message=str(error), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RequestCountView(APIView):
    """
        Description: API to get server request count
        GET /request-count/
        Responses:
            200: Request count retrieved successfully
            500: Server error
    """
    permission_classes = [AllowAny]

    def get(self,request):
        try:
            count = RequestCounterMiddleware.get_request_count()
            return success_response(data={"requests": count}, message=REQUEST_COUNT_FETCHED, status=status.HTTP_200_OK)
        except Exception as error:
            print('Error at get request count -->', error)
            return error_response(message=str(error), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class ResetRequestCountView(APIView):
    """
        Description: API to reset server request count

        POST /request-count/reset/
        Responses:
            200: Request count reset successfully
            500: Server error
    """
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            RequestCounterMiddleware.reset_request_count()
            return success_response(message=REQUEST_COUNT_RESET, status=status.HTTP_200_OK)
        except Exception as error:
            print('Error at reset request count -->', error)
            return error_response(message=str(error), status=status.HTTP_500_INTERNAL_SERVER_ERROR)