from django.urls import path

from .views.UserReset import UserReset

from .views.UserCreate import UserCreate
from .views.base import manifest
from .views.login import (
    Login,
    Logout,
    login_check,
)
from .views.password import (
    APIPasswordChange,
    APIPasswordResetView,
    APIPasswordResetConfirmView,
)
from .views.users import (
    APIUsersView, 
    UserUpdate,
    UserDelete
)

app_name = 'django_accounts_api'
urlpatterns = [
    path('', manifest, name='manifest'),

    path('check', login_check, name='login_check'),
    path('login', Login.as_view(), name='login'),
    path('logout', Logout.as_view(), name='logout'),

    path('password_change', APIPasswordChange.as_view(), name='password_change'),

    path('password_reset', APIPasswordResetView.as_view(), name='password_reset'),
    path('reset/<uidb64>/<token>/', APIPasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    path('users/', APIUsersView.as_view(), name='users'),
    path('user/<int:pk>/update', UserUpdate.as_view(), name='user_update'),
    path('user/<int:pk>/delete', UserDelete.as_view(), name='user_delete'),
    path('user/create', UserCreate.as_view(), name='user_create'),
    path('user/<int:pk>/reset', UserReset.as_view(), name='user_reset'),
]
