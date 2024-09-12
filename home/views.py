from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse

from core import settings
from home.emails import send_html_email_with_logo, send_welcome_email
from home.forms import LoginForm, RegistrationForm, UserPasswordChangeForm, UserPasswordResetForm, UserSetPasswordForm, \
    MemberForm, AssemblyForm, FundraisingProjectForm
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth import logout, login, authenticate

from django.views.generic import CreateView, TemplateView, ListView, UpdateView

from django.contrib.auth.decorators import login_required

from home.generators import random_password_generator
from home.models import Member, Church, Assembly, FundraisingProject
from home.search_filter import SearchFilter
from home.utils import AccessRequiredMixin


# Create your views here.
class HomeView(TemplateView, AccessRequiredMixin):
    template_name = "pages/dashboard.html"

    def get(self, request, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        else:
            return redirect('login')


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



# ==================== Assemblies ================

class AssemblyListView(AccessRequiredMixin, ListView, SearchFilter):
    model = Assembly
    template_name = "app/assemblies/list.html"
    paginate_by = settings.PAGE_SIZE
    paginator_class = Paginator
    required_roles = ["admin"]
    search_fields = ["name", ]
    total_count = 0

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            Q(church=self.request.user.assembly.church)
        )
        self.total_count = queryset.count()
        queryset = self.filter_queryset_here(request=self.request, queryset=queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total"] = self.total_count
        context["form"] = AssemblyForm(initial={"active": True, "church": self.request.user.assembly.church})
        return context

class NewAssemblyView(AccessRequiredMixin, CreateView):
    model = Member
    form_class = AssemblyForm
    template_name = "partials/assemblies/list/form.html"
    required_roles = ["admin"]

    def post(self, request, *args, **kwargs):
        form = AssemblyForm(request.POST, request.FILES)
        if form.is_valid():
            assembly = form.save(commit=True)
            messages.success(request, "Assembly has been successfully created")
            url = reverse("assembly_update", kwargs={"pk": assembly.id})
            response = render(request, "components/misc/redirect.html", {"url": url})
            response["HX-Retarget"] = "#success-url"
            return response
        else:
            print("errors", form.errors)
            return self.render_to_response(context={"form": form})

class EditAssemblyView(AccessRequiredMixin, UpdateView):
    model = Assembly
    form_class = AssemblyForm
    template_name = "app/assemblies/edit.html"
    required_roles = ["admin", "cashier"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = AssemblyForm(instance=self.object)
        return context

    def post(self, request, *args, **kwargs):
        assembly = self.get_object()
        form = AssemblyForm(request.POST, request.FILES, instance=assembly)

        if form.is_valid():
            member = form.save(commit=True)
            messages.success(request, "Assembly has been successfully updated")
            url = reverse("assembly_update", kwargs={"pk": member.id})
            response = render(request, "components/misc/redirect.html", {"url": url})
            response["HX-Retarget"] = "#success-url"
            return response
        else:
            print("errors", form.errors)
            return render(request, 'partials/assemblies/edit/modals/update.form.html',
                          {'form': form, 'object': assembly})

#==================== End Assemblies ==============
# ==================== Members ====================

class MemberListView(AccessRequiredMixin, ListView, SearchFilter):
    model = Member
    template_name = "app/members/list.html"
    paginate_by = settings.PAGE_SIZE
    paginator_class = Paginator
    required_roles = ["admin"]
    search_fields = ["first_name", "last_name", "phone_number", "email"]
    total_count = 0

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            Q(assembly__church=self.request.user.assembly.church)
        )

        if assembly_id := self.request.GET.get("assembly"):
            queryset = queryset.filter(assembly_id=assembly_id)

        self.total_count = queryset.count()
        queryset = self.filter_queryset_here(request=self.request, queryset=queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total"] = self.total_count
        context["form"] = MemberForm(initial={"is_active": True}, user=self.request.user)
        return context


class NewMemberView(AccessRequiredMixin, CreateView):
    model = Member
    form_class = MemberForm
    template_name = "partials/members/list/form.html"
    required_roles = ["admin"]

    def post(self, request, *args, **kwargs):
        form = MemberForm(request.POST, request.FILES, user=self.request.user)
        if form.is_valid():
            member = form.save(commit=False)
            member.role = "member"
            random_password = random_password_generator(8)
            # Set the password for the user
            member.set_password(random_password)

            member.save()

            send_welcome_email(member.email, member.first_name, random_password, member.assembly.church)
            messages.success(request, "Member has been successfully created")
            url = reverse("member_update", kwargs={"pk": member.id})
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
    required_roles = ["admin", "cashier"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = MemberForm(user=self.request.user, instance=self.object)
        return context

    def post(self, request, *args, **kwargs):
        member = self.get_object()
        form = MemberForm(request.POST, request.FILES, instance=member, user=self.request.user)

        if form.is_valid():
            member = form.save(commit=True)
            messages.success(request, "Member has been successfully updated")
            url = reverse("member_update", kwargs={"pk": member.id})
            response = render(request, "components/misc/redirect.html", {"url": url})
            response["HX-Retarget"] = "#success-url"
            return response
        else:
            print("errors", form.errors)
            return render(request, 'partials/members/edit/modals/update.form.html',
                          {'form': form, 'object': member})

#==================== End Members ==================
# =================== Fundraising Projects==========

class FundraisingProjectListView(AccessRequiredMixin, ListView, SearchFilter):
    model = FundraisingProject
    template_name = "app/projects/list.html"
    paginate_by = settings.PAGE_SIZE
    paginator_class = Paginator
    required_roles = ["admin"]
    search_fields = ["title", "description"]
    total_count = 0

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            Q(church=self.request.user.assembly.church)
        )
        self.total_count = queryset.count()
        queryset = self.filter_queryset_here(request=self.request, queryset=queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total"] = self.total_count
        context["form"] = FundraisingProjectForm(initial={"active": True, "church": self.request.user.assembly.church})
        return context

class NewFundraisingProjectView(AccessRequiredMixin, CreateView):
    model = FundraisingProject
    form_class = FundraisingProjectForm
    template_name = "partials/projects/list/form.html"
    required_roles = ["admin"]

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=True)
            messages.success(request, "Fundraising project has been successfully created")
            url = reverse("projects_update", kwargs={"pk": project.id})
            response = render(request, "components/misc/redirect.html", {"url": url})
            response["HX-Retarget"] = "#success-url"
            return response
        else:
            print("errors", form.errors)
            return self.render_to_response(context={"form": form})

class EditFundraisingProjectView(AccessRequiredMixin, UpdateView):
    model = FundraisingProject
    form_class = FundraisingProjectForm
    template_name = "app/projects/edit.html"
    required_roles = ["admin", "cashier"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.form_class(instance=self.object)
        return context

    def post(self, request, *args, **kwargs):
        project = self.get_object()
        form = self.form_class(request.POST, request.FILES, instance=project)

        if form.is_valid():
            project = form.save(commit=True)
            messages.success(request, "Fundraising project  has been successfully updated")
            url = reverse("projects_update", kwargs={"pk": project.id})
            response = render(request, "components/misc/redirect.html", {"url": url})
            response["HX-Retarget"] = "#success-url"
            return response
        else:
            print("errors", form.errors)
            return render(request, 'partials/assemblies/edit/modals/update.form.html',
                          {'form': form, 'object': project})

def send_test_email(request):
    subject = 'Test Email'
    message = 'This is a test email sent from Django.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = ['recipient@example.com']
    church = Church.objects.filter(logo__isnull=False).first()
    # Send the email
    send_html_email_with_logo('recipient@example.com', "John", church)

    return HttpResponse('Test email sent successfully!')
