from xml.dom import ValidationErr
from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from api.models import User
from api.utils import Util


class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'},
                                      write_only=True)

    class Meta:
        model = User
        fields = ['email', 'name', 'contact', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    # validating password and confirm password
    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')
        if password != password2:
            raise serializers.ValidationError("Password does not match.")
        return data

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=220)

    class Meta:
        model = User
        fields = ['email', 'password']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'contact']


class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=220, style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(
        max_length=220, style={'input_type': 'password'}, write_only=True)

    class Meta:
        fields = ['password', 'password2']

    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')
        user = self.context.get('user')
        if password != password2:
            raise serializers.ValidationError("Password does not match.")
        user.set_password(password)
        user.save()
        return data


class ResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=220)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            user_id = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            link = 'http://localhost:3000/api/user/reset' + user_id + '/' + token
            # send email
            body = 'Click on the link below to Reset Your Password.'
            data = {
                'subject': 'Reset Your Password',
                'body': body,
                'to_email': user.email
            }
            Util.send_email(data)
            return attrs
        else:
            raise ValidationErr('The given email is not registered. ')


class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=220, style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(
        max_length=220, style={'input_type': 'password'}, write_only=True)

    class Meta:
        fields = ['password', 'password2']

    def validate(self, data):
        try:
            password = data.get('password')
            password2 = data.get('password2')
            user_id = self.context.get('user_id')
            token = self.context.get('token')

            if password != password2:
                raise serializers.ValidationError("Password does not match.")
            id = smart_str(urlsafe_base64_decode(user_id))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise ValidationError('Token is not valid or is expired.')

            user.set_password(password)
            user.save()
            return data

        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, token)
            raise ValidationError('Token is not valid or is expired.')

class DrowsinessPredictionSerializer(serializers.Serializer):
    image_file = serializers.ImageField(required=True)
    
    def validate_image_file(self, value):
        return value

    class Meta:
        fields = ['image_file',]

class CsrfSerializer(serializers.Serializer):
    csrf_token = serializers.CharField()

    class Meta:
        fields = ['csrf_token',]