from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, UsernameField, \
    PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from home.models import Member, Assembly, FundraisingProject, PaymentMethod, Payment


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(label=_('First Name'), max_length=50, required=True)
    last_name = forms.CharField(label=_('Last Name'), max_length=50, required=True)
    email = forms.EmailField(label=_('Email'), required=True)
    phone_number = forms.CharField(label=_('Phone Number'), max_length=50, required=True)
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password'}),
    )
    password2 = forms.CharField(
        label=_("Password Confirmation"),
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password Confirmation'}),
    )
    assembly = forms.ModelChoiceField(
        queryset=Assembly.objects.filter(
            Q(active=True) &
            Q(church__active=True)
        ),
    )

    class Meta:
        model = Member
        fields = [
            "first_name",
            "email",
            "last_name",
            "assembly",
            "phone_number",
            "sex",
            "date_of_birth",
        ]

        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email'
            })
        }


class LoginForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={
        "placeholder": "Email Address",

    }))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            "placeholder": "Password",
            "autocomplete": "current-password"
        }),
    )


class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'Email'
    }))

    def clean(self):
        data = super().clean()
        email = data.get("email")
        if email:
            if not Member.objects.filter(email=email).exists():
                raise forms.ValidationError({"email": "Email is not registered"})



class UserSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'placeholder': 'New Password',
                       "autocomplete": "new-password"
    }), label="New Password")
    new_password2 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm New Password',
        "autocomplete": "new-password"
    }), label="Confirm New Password")


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'placeholder': 'Old Password'
    }), label='Old Password')
    new_password1 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'placeholder': 'New Password'
    }), label="New Password")
    new_password2 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm New Password'
    }), label="Confirm New Password")


# Member
class MemberForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        queryset = Assembly.objects.none()
        if "user" in kwargs:
            print("here", kwargs.get("user"))
            user = kwargs.pop("user")
            queryset = Assembly.objects.filter(
                Q(active=True) &
                Q(church__active=True) &
                Q(church=user.assembly.church)
            )
        super().__init__(*args, **kwargs)
        self.fields["assembly"] = forms.ModelChoiceField(
            queryset=queryset
        )

    first_name = forms.CharField(label=_('First Name'), max_length=50, required=True)
    last_name = forms.CharField(label=_('Last Name'), max_length=50, required=True)
    email = forms.EmailField(label=_('Email'), required=True)
    phone_number = forms.CharField(label=_('Phone Number'), max_length=50, required=True)
    # password1 = forms.CharField(
    #     label=_("Password"),
    #     widget=forms.PasswordInput(attrs={
    #         'placeholder': 'Password'}),
    # )
    # password2 = forms.CharField(
    #     label=_("Password Confirmation"),
    #     widget=forms.PasswordInput(attrs={
    #         'placeholder': 'Password Confirmation'}),
    # )

    address = forms.CharField(max_length=255, widget=forms.Textarea(attrs={
        "rows": 3,
    }))

    class Meta:
        model = Member
        exclude = ["password", "date_joined", "role"]
        widgets = {
            "email": forms.EmailInput(attrs={"type": "email", "placeholder": "Email"}),
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
        }


class AssemblyForm(forms.ModelForm):
    class Meta:
        model = Assembly
        exclude = ["date_joined"]
        widgets = {
            "location": forms.Textarea(attrs={"rows": 3})
        }


class PaymentMethodForm(forms.ModelForm):
    initial_balance = forms.DecimalField(max_digits=11, min_value=0, decimal_places=2, label="Initial Balance")

    class Meta:
        model = PaymentMethod
        exclude = ["total_balance", "available_balance"]
        # widgets = {
        #     "location": forms.Textarea(attrs={"rows": 3})
        # }


class FundraisingProjectForm(forms.ModelForm):
    def clean(self):
        data = super().clean()
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        if end_date < start_date:
            raise forms.ValidationError({"end_date": "End date must be greater than start date"})
        if end_date < timezone.now().today().date():
            raise forms.ValidationError({"end_date": "End date must be in the future"})

    class Meta:
        model = FundraisingProject
        exclude = ["raised_amount"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }


class PaymentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        queryset = FundraisingProject.objects.none()
        member_queryset = Member.objects.none()
        method_queryset = PaymentMethod.objects.none()
        if "user" in kwargs:
            user = kwargs.pop("user")
            queryset = FundraisingProject.objects.filter(
                Q(active=True) & Q(end_date__gte=timezone.now().date()) &
                Q(church=user.assembly.church)
            )
            method_queryset = PaymentMethod.objects.filter(
                Q(active=True)&
                Q(church=user.assembly.church)
            )
            member_queryset = Member.objects.filter(
                Q(is_active=True) &
                Q(assembly__church=user.assembly.church)
            )

        super().__init__(*args, **kwargs)
        self.fields["funderRaisingProject"] = forms.ModelChoiceField(queryset=queryset, required=False, label="Fundraising Project")
        self.fields["member"] = forms.ModelChoiceField(queryset=member_queryset, label="Member")
        self.fields["payment_method"] = forms.ModelChoiceField(queryset=method_queryset, label="Payment Method")

    def clean(self):
        data = super().clean()
        payment_type = data.get("type")
        funderRaisingProject = data.get("funderRaisingProject")
        if payment_type == "Fundraising Contribution" and funderRaisingProject in [None, ""] :
            raise forms.ValidationError({"funderRaisingProject": "Select a Fundraising Project"})

    class Meta:
        model = Payment
        fields = "__all__"
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }
