from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.UserRegistrationView.as_view(), name='register'),
    path('auth/login/', views.UserLoginView.as_view(), name='login'),
    path('auth/logout/', views.user_logout_view, name='logout'),
    path('auth/change-password/', views.UserPasswordChangeView.as_view(), name='change-password'),
    
    # Profile endpoints
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    
    # Public user endpoints
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<uuid:id>/', views.UserDetailView.as_view(), name='user-detail'),
] 