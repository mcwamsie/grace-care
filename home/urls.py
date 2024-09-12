from django.contrib.auth import views as auth_views
from django.urls import path

from home.views import HomeView, MemberListView, EditMemberView, NewMemberView, UserLoginView, logout_view, \
    UserRegistration, UserPasswordChangeView, \
    FundraisingProjectListView, NewFundraisingProjectView, EditFundraisingProjectView, \
    UserPasswordResetView, UserPasswordResetConfirmView, billing, DashboardView, send_test_email, AssemblyListView, \
    NewAssemblyView, EditAssemblyView, PaymentMethodListView, NewPaymentMethodView, EditPaymentMethodView

urlpatterns = [
    path('test/', send_test_email, name='test'),
    path('', HomeView.as_view(), name='index'),
    path('billing', billing, name='billing'),
    path('profile', billing, name='profile'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    path('members/', MemberListView.as_view(), name='member_list'),
    path('members/new/', NewMemberView.as_view(), name='member_add'),
    path('members/update/<int:pk>/', EditMemberView.as_view(), name='member_update'),

    # Assemblies
    path('assemblies/', AssemblyListView.as_view(), name='assembly_list'),
    path('assemblies/new/', NewAssemblyView.as_view(), name='assembly_add'),
    path('assemblies/update/<int:pk>/', EditAssemblyView.as_view(), name='assembly_update'),

    # Fundraising Projects
    path('funderaising-projects/', FundraisingProjectListView.as_view(), name='projects_list'),
    path('funderaising-projects/new/', NewFundraisingProjectView.as_view(), name='projects_add'),
    path('funderaising-projects/update/<int:pk>/', EditFundraisingProjectView.as_view(), name='projects_update'),

    # Fundraising Projects
    path('payment-methods/', PaymentMethodListView.as_view(), name='methods_list'),
    path('payment-methods/new/', NewPaymentMethodView.as_view(), name='methods_add'),
    path('payment-methods/update/<int:pk>/', EditPaymentMethodView.as_view(), name='methods_update'),

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
