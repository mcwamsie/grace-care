from django.urls import path
from django.contrib.auth import views as auth_views

from home.views import HomeView, MemberListView, EditMemberView, NewMemberView, UserLoginView, logout_view, UserRegistration, UserPasswordChangeView, \
    UserPasswordResetView, UserPasswordResetConfirmView, billing, DashboardView

urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    path('billing', billing, name='billing'),
    path('profile', billing, name='profile'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),


    path('members/', MemberListView.as_view(), name='member_list'),
    path('members/new/', NewMemberView.as_view(), name='member_add'),
    path('members/update/<int:pk>/', EditMemberView.as_view(), name='member_update'),


        # Authentication
    path('accounts/login/', UserLoginView.as_view(), name='login'),
    path('accounts/logout/', logout_view, name='logout'),
    path('accounts/register/', UserRegistration.as_view(), name='register'),
    path('accounts/password-change/', UserPasswordChangeView.as_view(), name='password_change'),
    path('accounts/password-change-done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'
    ), name="password_change_done"),
    path('accounts/password-reset/', UserPasswordResetView.as_view(), name='password_reset'),
    path('accounts/password-reset-confirm/<uidb64>/<token>/',
        UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/password-reset-done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('accounts/password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
]
