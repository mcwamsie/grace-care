from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse

from core import settings
from home.forms import LoginForm, RegistrationForm, UserPasswordChangeForm, UserPasswordResetForm, UserSetPasswordForm, \
    MemberForm
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth import logout, login, authenticate

from django.views.generic import CreateView, TemplateView, ListView, UpdateView

from django.contrib.auth.decorators import login_required

from home.models import Member
from home.search_filter import SearchFilter
from home.utils import AccessRequiredMixin


# Create your views here.
class HomeView(TemplateView, AccessRequiredMixin):
    template_name = "pages/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['parent'] = 'pages'
        context['segment'] = 'index'
        return context


@login_required(login_url="/accounts/login/")
def dashboard(request):
    context = {
        'parent': 'pages',
        'segment': 'billing'
    }
    return render(request, '', context)


class DashboardView(AccessRequiredMixin, TemplateView):
    template_name = "app/dashboard.html"


@login_required(login_url="/accounts/login/")
def billing(request):
    context = {
        'parent': 'pages',
        'segment': 'billing'
    }
    return render(request, 'pages/billing.html', context)


@login_required(login_url="/accounts/login/")
def profile(request):
    context = {
        'parent': 'pages',
        'segment': 'profile'
    }
    return render(request, 'pages/profile.html', context)


# Authentication
class UserLoginView(LoginView):
    template_name = 'accounts/sign-in.html'
    form_class = LoginForm


class UserRegistration(CreateView):
    template_name = 'accounts/sign-up.html'
    form_class = RegistrationForm
    success_url = "/accounts/login/"

    def form_valid(self, form):
        member = form.save(commit=False)
        member.role = "member"
        member.is_active = True
        member.is_staff = False
        member.is_superuser = False
        member.save()

        raw_password = form.cleaned_data.get('password1')
        user = authenticate(username=member.email, password=raw_password)

        if user is not None:
            # Log the user in
            messages.success(self.request, "Welcome to Grace Care!")
            login(self.request, user)
            return redirect('dashboard')
        return redirect('dashboard')
    # def post(self, request, *args, **kwargs):
    #     form = self.form_class(request.POST)
    #     if form.is_valid():
    #
    #     else:
    #         messages.error(self.request, 'Please correct the error below.')
    #         return self.form_invalid(form)


def logout_view(request):
    logout(request)
    return redirect('/accounts/login/')


class UserPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    form_class = UserPasswordResetForm


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    form_class = UserSetPasswordForm


class UserPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    form_class = UserPasswordChangeForm


# Members

class MemberListView(AccessRequiredMixin, ListView, SearchFilter):
    model = Member
    template_name = "app/members/list.html"
    paginate_by = settings.PAGE_SIZE
    paginator_class = Paginator
    required_roles = ["admin"]
    search_fields = ["name", ]
    total_count = 0

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            Q(assembly__church=self.request.user.assembly.church)
        )
        self.total_count = queryset.count()
        queryset = self.filter_queryset_here(request=self.request, queryset=queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total"] = self.total_count
        return context


class NewMemberView(AccessRequiredMixin, CreateView):
    model = Member
    form_class = MemberForm
    template_name = "partials/members/list/form.html"
    required_roles = ["A"]

    def post(self, request, *args, **kwargs):
        form = MemberForm(request.POST, request.FILES)
        if form.is_valid():
            member = form.save(commit=True)
            messages.success(request, "Package has been successfully created")
            url = reverse("members_edit", kwargs={"pk": member.id})
            response = render(request, "components/misc/redirect.html", {"url": url})
            response["HX-Retarget"] = "#success-url"
            return response
        else:
            print("errors", form.errors)
            return self.render_to_response(context={"form": form})


class EditMemberView(AccessRequiredMixin, UpdateView):
    model = Member
    form_class = MemberForm
    template_name = "app/members/edit.html"
    required_roles = ["D", "A"]

    def post(self, request, *args, **kwargs):
        package = self.get_object()
        form = MemberForm(request.POST, request.FILES, instance=package)

        if form.is_valid():
            package = form.save(commit=True)
            messages.success(request, "Package has been successfully updated")
            url = reverse("packages_edit", kwargs={"pk": package.id})
            response = render(request, "components/misc/redirect.html", {"url": url})
            response["HX-Retarget"] = "#success-url"
            return response
        else:
            print("errors", form.errors)
            return render(request, 'partials/members/edit/modals/update.form.html',
                          {'form': form, 'object': package})
