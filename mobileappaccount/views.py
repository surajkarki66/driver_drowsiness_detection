from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.authentication import JWTAuthentication
from mobileappaccount.serializers import (UserRegistrationSerializer,
                                          UserLoginSerializer, UserProfileSerializer, ChangePasswordSerializer,
                                          ResetPasswordEmailSerialier, UserPasswordResetSerializer, DrowsinessPredictionSerializer)
from mobileappaccount.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .utils import classify_image
from webappaccount.models import Log



def get_user_token(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserRegisteration(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        print(request.data,
              "ABCD Userdata *****************************************************8 ")
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer, "ABCD serializer data -----------------------------------------------------------------")

        user = serializer.save()
        token = get_user_token(user)
        print(token, "ABCD token data -----------------------------------------------------------------")

        return Response({'token': token, 'msg': 'Registeration Success'},
                        status=status.HTTP_201_CREATED)


class LoginView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
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
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangePassword (APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = ChangePasswordSerializer(data=request.data,
                                              context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Password changed successfully.'}, status=status.HTTP_200_OK)


class ResetPasswordEmail(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = ResetPasswordEmailSerialier(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Link to reset password is sent. Please check your email.'},
                        status=status.HTTP_200_OK)


class UserPasswordReset(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, user_id, token, format=None):
        serializer = UserPasswordResetSerializer(data=request.data,
                                                 context={'user_id': user_id, 'token': token})
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Password Reset Successfully'},
                        status=status.HTTP_200_OK)

class DrowsinessPredictionView(APIView):
    serializer_class = DrowsinessPredictionSerializer

    def post(self, request, format=None):
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
