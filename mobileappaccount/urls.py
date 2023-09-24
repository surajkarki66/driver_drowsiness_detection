
from django.urls import path, include
from mobileappaccount.views import (UserRegisteration,
                                    LoginView, UserProfile,
                                    ChangePassword, ResetPasswordEmail, UserPasswordReset, DrowsinessPredictionView)

urlpatterns = [
    path('register/', UserRegisteration.as_view(),
         name='register'),
    path('login/', LoginView.as_view(),
         name='login'),
    path('profile/', UserProfile.as_view(),
         name='profile'),
    path('changepassword/', ChangePassword.as_view(),
         name='changepassword'),
    path('reset-password-email/', ResetPasswordEmail.as_view(),
         name='reset-password-email'),
    path('reset-password/<user_id>/<token>/', UserPasswordReset.as_view(),
         name='reset-password'),
    path('predict/', DrowsinessPredictionView.as_view(), name='predict-drowsiness')
]
