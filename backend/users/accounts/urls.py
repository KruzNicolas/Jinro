
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import RegisterUserView, UserDetailView, UserUpdateView, PasswordResetRequestView, PasswordResetConfirmView, DeleteUserView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', UserDetailView.as_view(), name='user_detail'),
    path('update/', UserUpdateView.as_view(), name='user_update'),
    path('forgot-password/', PasswordResetRequestView.as_view(),
         name='forgot_password'),
    path('reset-password-confirm/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(), name='reset_password_confirm'),
    path('delete/', DeleteUserView.as_view(), name='delete-account'),
]
