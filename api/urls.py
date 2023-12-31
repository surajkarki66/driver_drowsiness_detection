
from django.urls import path

from api.views import (UserRegistration,
                                    LoginView, UserProfile, CSRF,
                                    ChangePassword, ResetPasswordEmail, UserPasswordReset, DrowsinessPredictionView)

urlpatterns = [
    path('register/', UserRegistration.as_view(),
         name='register'),
    path('login/', LoginView.as_view(),
         name='login'),
    path('profile/', UserProfile.as_view(),
         name='profile'),
    path('changepassword/', ChangePassword.as_view(),
         name='changepassword'),
    path('reset-password-email/', ResetPasswordEmail.as_view(),
         name='reset-password-email'),
    path('reset-password/<int:id>/<str:token>/', UserPasswordReset.as_view(),
         name='reset-password'),
    path('csrf/', CSRF.as_view(), name='csrf-api'),
    path('predict/', DrowsinessPredictionView.as_view(), name='predict-drowsiness')
]
