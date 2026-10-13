from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="We'll use this for your order updates.")
    first_name = forms.CharField(max_length=150, required=True, label="Full name")

    class Meta:
        model = User
        fields = ("username", "first_name", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=160, label="Full name")
    email = forms.EmailField()
    phone = forms.CharField(max_length=30, label="Phone number")
    address = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), label="Delivery address")
    city = forms.CharField(max_length=100)
    postal_code = forms.CharField(max_length=20, label="PIN / postal code")
    payment_method = forms.ChoiceField(
        choices=[("COD", "Cash on delivery")],
        widget=forms.RadioSelect,
        initial="COD",
        label="Payment method",
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user and not self.is_bound:
            self.fields["full_name"].initial = user.get_full_name() or user.username
            self.fields["email"].initial = user.email
        for field in self.fields.values():
            if not isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs.setdefault("class", "form-control")
