# shop/forms.py

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class CustomerRegistrationForm(UserCreationForm):

    # Trường email
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập địa chỉ email'
        })
    )

    # Trường họ
    first_name = forms.CharField(
        required=True,
        label="Họ",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ví dụ: Nguyễn'
        })
    )

    # Trường tên
    last_name = forms.CharField(
        required=True,
        label="Tên",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ví dụ: Văn An'
        })
    )

    class Meta:
        model = User

        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
            'password1',
            'password2',
        )

        labels = {
            'username': 'Tên đăng nhập',
            'password1': 'Mật khẩu',
            'password2': 'Xác nhận mật khẩu',
        }

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập tên đăng nhập'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email').strip().lower()

        # Kiểm tra email đã được tài khoản khác sử dụng chưa
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Địa chỉ email này đã được sử dụng."
            )

        return email

    def save(self, commit=True):
        user = super().save(commit=False)

        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        # Tài khoản khách hàng không có quyền quản trị
        user.is_staff = False
        user.is_superuser = False

        if commit:
            user.save()

        return user