from django.contrib.auth import views as imp
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path(
        'logout/',
        imp.LogoutView.as_view(
            template_name='users/logged_out.html'
        ),
        name='logout'
    ),
    path(
        'login/',
        imp.LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    # Смена пароля
    path(
        'password_change/',
        imp.PasswordChangeView.as_view(
            template_name='users/password_change_form.html'
        ),
        name='password_change'
    ),
    # Сообщение об успешном изменении пароля
    path(
        'password_change/done/',
        imp.PasswordChangeDoneView.as_view(
            template_name='users/password_change_done.html'
        ),
        name='password_change_done'
    ),
    # Восстановление пароля
    path(
        'password_reset/',
        imp.PasswordResetView.as_view(
            template_name='users/password_reset_form.html'
        ),
        name='password_reset'
    ),
    # Сообщение об отправке ссылки для восстановления пароля
    path(
        'password_reset/done/',
        imp.PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    # Вход по ссылке для восстановления пароля
    path(
        'reset/<uidb64>/<token>/',
        imp.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),
    # Сообщение об успешном восстановлении пароля
    path(
        'reset/done/',
        imp.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]
