import datetime

import month
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
    MemberForm, AssemblyForm, FundraisingProjectForm, PaymentMethodForm, PaymentForm
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth import logout, login, authenticate

from django.views.generic import CreateView, TemplateView, ListView, UpdateView, DetailView

from django.contrib.auth.decorators import login_required

from home.generators import random_password_generator
from home.models import Member, Church, Assembly, FundraisingProject, PaymentMethod, MonthlySubscription, Payment, \
    FundraisingContribution
from home.search_filter import SearchFilter
from home.utils import AccessRequiredMixin, calculateContributions


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.role == "admin":
            context['members'] = Member.objects.filter(Q(assembly__church=self.request.user.assembly.church)).count()
            context['assemblies'] = Assembly.objects.filter(Q(church=self.request.user.assembly.church)).count()
            context['projects'] = FundraisingProject.objects.filter(Q(church=self.request.user.assembly.church)).count()
            context['fundraisingProjects'] = FundraisingProject.objects.filter(Q(church=self.request.user.assembly.church))
            context['methods'] = PaymentMethod.objects.filter(Q(church=self.request.user.assembly.church))
            return context
        else:
            context['methods'] = PaymentMethod.objects.filter(Q(church=self.request.user.assembly.church))
            return context



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

    #def form_valid(self, form):


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
    required_roles = ["admin"]

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
    required_roles = ["admin"]

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
# =================== Fundraising Projects ==========

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
    required_roles = ["admin"]

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
            return render(request, 'partials/projects/edit/modals/update.form.html',
                          {'form': form, 'object': project})


#==================== End Fundraising Projects======
# =================== Payment Methods ==========

class PaymentMethodListView(AccessRequiredMixin, ListView, SearchFilter):
    model = PaymentMethod
    template_name = "app/methods/list.html"
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
        context["form"] = PaymentMethodForm(initial={"active": True, "church": self.request.user.assembly.church})
        return context


class NewPaymentMethodView(AccessRequiredMixin, CreateView):
    model = PaymentMethod
    form_class = PaymentMethodForm
    template_name = "partials/methods/list/form.html"
    required_roles = ["admin"]

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            method = form.save(commit=False)
            initial_balance = form.cleaned_data["initial_balance"]
            method.available_balance = initial_balance
            method.total_balance = initial_balance
            method.save()
            messages.success(request, self.model._meta.verbose_name + " has been successfully created")
            url = reverse("methods_update", kwargs={"pk": method.id})
            response = render(request, "components/misc/redirect.html", {"url": url})
            response["HX-Retarget"] = "#success-url"
            return response
        else:
            print("errors", form.errors)
            return self.render_to_response(context={"form": form})


class EditPaymentMethodView(AccessRequiredMixin, UpdateView):
    model = PaymentMethod
    form_class = PaymentMethodForm
    template_name = "app/methods/edit.html"
    required_roles = ["admin"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.form_class(instance=self.object, initial={"initial_balance": 0})
        return context

    def post(self, request, *args, **kwargs):
        method = self.get_object()
        form = self.form_class(request.POST, request.FILES, instance=method)

        if form.is_valid():
            method = form.save(commit=True)
            messages.success(request, self.model._meta.verbose_name + " has been successfully updated")
            url = reverse("methods_update", kwargs={"pk": method.id})
            response = render(request, "components/misc/redirect.html", {"url": url})
            response["HX-Retarget"] = "#success-url"
            return response
        else:
            print("errors", form.errors)
            return render(request, 'partials/methods/edit/modals/update.form.html',
                          {'form': form, 'object': method})


# ==================== End Payment Methods======
# =================== Monthly Subscription ==========

class SubscriptionListView(AccessRequiredMixin, ListView, SearchFilter):
    model = Member
    template_name = "app/subscriptions/list.html"
    paginate_by = settings.PAGE_SIZE
    paginator_class = Paginator
    required_roles = ["admin", "cashier"]
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
        today = datetime.datetime.today()
        m = month.Month(today.year, today.month)
        m2 = m - 4

        last5Months = m2.range(m)
        # self.last5Months = self.last5Months

        last5Months.reverse()
        if self.request.GET.get("refresh"):
            for member in self.get_queryset():
                calculateContributions(member=member)
        subscriptions = MonthlySubscription.objects.filter(
            Q(member__in=self.get_queryset()) &
            Q(subscription_month__in=last5Months)
        )

        #print("subscriptions", subscriptions)

        context = super().get_context_data(**kwargs)
        context["subscriptions"] = subscriptions
        context["last5Months"] = last5Months
        context["total"] = self.total_count
        context["form"] = MemberForm(initial={"is_active": True}, user=self.request.user)
        return context


# ==================== End Monthly Subscription======
# =================== Payments ======================

class PaymentListView(AccessRequiredMixin, ListView, SearchFilter):
    model = Payment
    template_name = "app/payments/list.html"
    paginate_by = settings.PAGE_SIZE
    paginator_class = Paginator
    required_roles = ["admin", "cashier", "member"]
    search_fields = ["member__first_name", "member__last_name"]
    total_count = 0

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            Q(member__assembly__church=self.request.user.assembly.church)
        )

        if self.request.user.role == "member":
            queryset = super().get_queryset().filter(
                Q(member=self.request.user)
            )

        self.total_count = queryset.count()
        queryset = self.filter_queryset_here(request=self.request, queryset=queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total"] = self.total_count
        context["form"] = PaymentForm(initial={"active": True}, user=self.request.user)
        return context


class NewPaymentView(AccessRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = "partials/payments/list/form.html"
    required_roles = ["admin"]

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES, user=self.request.user)
        if form.is_valid():
            payment = form.save(commit=True)
            if payment.type == "Fundraising Contribution":
                project = form.cleaned_data["funderRaisingProject"]
                FundraisingContribution.objects.create(
                    project=project,
                    payment=payment,
                    amount=payment.amount,
                    date=payment.date,
                )
                project.raised_amount += payment.amount
                project.save()
            elif payment.type == "Monthly Subscription":
                payment.apply_to_subscriptions()

            payment.payment_method.available_balance += payment.amount
            payment.payment_method.total_balance += payment.amount
            payment.payment_method.save()

            messages.success(request, self.model._meta.verbose_name + " has been successfully created")
            url = reverse("payments_list")
            response = render(request, "components/misc/redirect.html", {"url": url})
            response["HX-Retarget"] = "#success-url"
            return response
        else:
            print("errors", form.errors)
            return self.render_to_response(context={"form": form})


class EditPaymentView(AccessRequiredMixin, DetailView):
    model = Payment
    # form_class = PaymentMethodForm
    template_name = "app/payments/edit.html"
    required_roles = ["admin", "cashier"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context["form"] = self.form_class(instance=self.object, initial={"initial_balance": 0})
        return context

    def post(self, request, *args, **kwargs):
        method = self.get_object()
        form = self.form_class(request.POST, request.FILES, instance=method)

        if form.is_valid():
            method = form.save(commit=True)
            messages.success(request, self.model._meta.verbose_name + " has been successfully updated")
            url = reverse("methods_update", kwargs={"pk": method.id})
            response = render(request, "components/misc/redirect.html", {"url": url})
            response["HX-Retarget"] = "#success-url"
            return response
        else:
            print("errors", form.errors)
            return render(request, 'partials/methods/edit/modals/update.form.html',
                          {'form': form, 'object': method})


# =================== End Payments =================

def send_test_email(request):
    subject = 'Test Email'
    message = 'This is a test email sent from Django.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = ['recipient@example.com']
    church = Church.objects.filter(logo__isnull=False).first()
    # Send the email
    send_html_email_with_logo('recipient@example.com', "John", church)

    return HttpResponse('Test email sent successfully!')
