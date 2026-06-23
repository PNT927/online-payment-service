from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render

from payapp.models import Account
from .forms import RegisterForm


INITIAL_GBP_BALANCE = Decimal("500.00")

GBP_TO_TARGET = {
    "GBP": Decimal("1.00"),
    "USD": Decimal("1.25"),
    "EUR": Decimal("1.15"),
}


def register_user(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.email = form.cleaned_data["email"]
            user.save()

            chosen_currency = form.cleaned_data["currency"]
            initial_balance = (INITIAL_GBP_BALANCE * GBP_TO_TARGET[chosen_currency]).quantize(
                Decimal("0.01")
            )

            Account.objects.create(
                user=user,
                currency=chosen_currency,
                balance=initial_balance,
            )

            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("user_dashboard")
        else:
            messages.error(request, "Registration unsuccessful. Please correct the errors below.")
    else:
        form = RegisterForm()

    return render(request, "register/register.html", {"register_form": form})


def login_user(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "Login successful.")

                if user.is_staff or user.is_superuser:
                    return redirect("admin_dashboard")
                return redirect("user_dashboard")

        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, "register/login.html", {"login_form": form})


def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")