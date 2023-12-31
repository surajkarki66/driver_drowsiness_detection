
from django.urls import path

from webapp.views import *

urlpatterns = [
    path('', LandingPage, name='landing_page'),
    path('live_detection/', LiveDetectionPage, name='live_detection'),
    path('live_detection/start_camera/', start_camera, name='start_camera'),
    path('live_detection/stop_camera/', stop_camera, name='stop_camera'),
    path('signup/', SignupPage, name='signup'),
    path('login/', LoginPage, name='login'),
    path('logout/', LogoutPage, name='logout'),
]
