
from django.urls import path

from webappaccount.views import *

urlpatterns = [
    path('', HomePage, name='home'),
    path('start_camera/', start_camera, name='start_camera'),
    path('stop_camera/', stop_camera, name='stop_camera'),
    path('signup/', SignupPage, name='signup'),
    path('login/', LoginPage, name='login'),
    path('logout/', LogoutPage, name='logout'),
    path('process_image/', process_image, name='process_image'),

]
