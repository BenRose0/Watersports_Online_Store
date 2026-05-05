from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'customer'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='customer/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]