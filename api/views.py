from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.middleware.csrf import get_token
from drf_spectacular.utils import extend_schema
from django.views.decorators.csrf import csrf_protect
from rest_framework.decorators import api_view


from api.serializers import (UserRegistrationSerializer,CsrfSerializer,
                                          UserLoginSerializer, UserProfileSerializer, ChangePasswordSerializer,
                                          ResetPasswordEmailSerializer, UserPasswordResetSerializer, DrowsinessPredictionSerializer)
from api.renderers import UserRenderer

from .utils import classify_image
from webapp.models import Log


class CSRF(APIView):
    serializer_class = CsrfSerializer

    @extend_schema(summary='Get CSRF Token', tags=['Api'])
    def get(self, request, *args, **kwargs):
        csrf_token = get_token(request)
        csrf = {
            "csrf_token": csrf_token,
        }
        serializer = self.serializer_class(data = csrf)
        serializer.is_valid(raise_exception=True)

        response = JsonResponse({"csrfToken": serializer.data.get('csrf_token')})
        return response

def get_user_token(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@method_decorator(csrf_protect, name='dispatch')
class UserRegistration(APIView):
    renderer_classes = [UserRenderer]
    serializer_class = UserRegistrationSerializer

    @extend_schema(summary='User signup', tags=['Api'])
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = get_user_token(user)

        return Response({'token': token, 'msg': 'Registration Success'},
                        status=status.HTTP_201_CREATED)

@method_decorator(csrf_protect, name='dispatch')
class LoginView(APIView):
    renderer_classes = [UserRenderer]
    serializer_class = UserLoginSerializer
    
    @extend_schema(summary="User Login", tags=["Api"])
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            token = get_user_token(user)

            user = {'email': user.email, 'username': user.name, 'contact': user.contact}
            response = Response({'token': token, 'msg': 'Login Success', 'user': user}, status=status.HTTP_200_OK)
            response.set_cookie(key='jwt', value=token['access'])
            return response
        else:
            return Response({'errors': {'non_field_errors': ['Incorrect email or password']}},
                            status=status.HTTP_404_NOT_FOUND)


class UserProfile(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated,]
    serializer_class = UserProfileSerializer
    @extend_schema(summary='User profile', tags=['Api'])
    def get(self, request):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

@method_decorator(csrf_protect, name='dispatch')
class ChangePassword (APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    @extend_schema(summary='Password change', tags=['Api'])
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data,
                                              context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Password changed successfully.'}, status=status.HTTP_200_OK)

@method_decorator(csrf_protect, name='dispatch')
class ResetPasswordEmail(APIView):
    renderer_classes = [UserRenderer]
    serializer_class = ResetPasswordEmailSerializer
    @extend_schema(summary='Reset password email', tags=['Api'])
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Link to reset password is sent. Please check your email.'},
                        status=status.HTTP_200_OK)

@method_decorator(csrf_protect, name='dispatch')
class UserPasswordReset(APIView):
    renderer_classes = [UserRenderer]
    serializer_class = UserPasswordResetSerializer
    lookup_field = 'id'

    @extend_schema(summary='User password reset', tags=['Api'])
    def post(self, request, id, token):
        serializer = self.serializer_class(data=request.data,
                                                 context={'id': id, 'token': token})
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Password Reset Successfully'},
                        status=status.HTTP_200_OK)

@method_decorator(csrf_protect, name='dispatch')
class DrowsinessPredictionView(APIView):
    serializer_class = DrowsinessPredictionSerializer

    @extend_schema(summary='Drowsiness prediction', tags=['Api'])
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        image = serializer.validated_data['image_file']
        result = classify_image(image)
        token = request.COOKIES.get('jwt')
        jwt_authentication = JWTAuthentication()
        decoded_token = jwt_authentication.get_validated_token(token)

        # Extract the payload data
        payload = jwt_authentication.get_user(decoded_token)
        log_instance = Log(user=payload)
        log_instance.save_img(image)

        return Response(result)
