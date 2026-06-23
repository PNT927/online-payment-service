from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Account, Notification, PaymentRequest, PaymentTransaction

from decimal import Decimal
from urllib.request import urlopen
import json

from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User
from .forms import DirectPaymentForm, PaymentRequestForm
from register.forms import CreateAdminForm
from django.core.mail import send_mail

def convert_currency(from_currency, to_currency, amount):
    url = f"http://127.0.0.1:8000/webapps2026/conversion/{from_currency}/{to_currency}/{amount}/"
    response = urlopen(url)
    data = json.loads(response.read().decode("utf-8"))
    return Decimal(data["rate"]), Decimal(data["converted_amount"])


@login_required
def user_dashboard(request):
    account = Account.objects.get(user=request.user)

    recent_notifications = Notification.objects.filter(user=request.user).order_by("-created_at")[:5]

    recent_sent = PaymentTransaction.objects.filter(sender=request.user).order_by("-created_at")[:5]
    recent_received = PaymentTransaction.objects.filter(recipient=request.user).order_by("-created_at")[:5]

    recent_requests_made = PaymentRequest.objects.filter(requester=request.user).order_by("-created_at")[:5]
    recent_requests_received = PaymentRequest.objects.filter(target_user=request.user).order_by("-created_at")[:5]

    sent_count = PaymentTransaction.objects.filter(sender=request.user).count()
    received_count = PaymentTransaction.objects.filter(recipient=request.user).count()

    pending_requests = PaymentRequest.objects.filter(target_user=request.user, status="PENDING").count()
    accepted_requests = PaymentRequest.objects.filter(target_user=request.user, status="ACCEPTED").count()
    rejected_requests = PaymentRequest.objects.filter(target_user=request.user, status="REJECTED").count()

    context = {
        "account": account,
        "recent_notifications": recent_notifications,
        "recent_sent": recent_sent,
        "recent_received": recent_received,
        "recent_requests_made": recent_requests_made,
        "recent_requests_received": recent_requests_received,
        "sent_count": sent_count,
        "received_count": received_count,
        "pending_requests": pending_requests,
        "accepted_requests": accepted_requests,
        "rejected_requests": rejected_requests,
    }
    return render(request, "payapp/dashboard.html", context)

@login_required
def send_payment(request):
    if request.method == "POST":
        form = DirectPaymentForm(request.POST)

        if form.is_valid():
            recipient_email = form.cleaned_data["recipient_email"]
            amount = form.cleaned_data["amount"]

            if request.user.email == recipient_email:
                messages.error(request, "You cannot send money to yourself.")
                return render(request, "payapp/send_payment.html", {"form": form})

            try:
                recipient = User.objects.get(email=recipient_email)
            except User.DoesNotExist:
                messages.error(request, "Recipient does not exist.")
                return render(request, "payapp/send_payment.html", {"form": form})

            with transaction.atomic():
                sender_account = Account.objects.select_for_update().get(user=request.user)
                recipient_account = Account.objects.select_for_update().get(user=recipient)

                if sender_account.balance < amount:
                    messages.error(request, "Insufficient funds.")
                    return render(request, "payapp/send_payment.html", {"form": form})

                rate, converted_amount = convert_currency(
                    sender_account.currency,
                    recipient_account.currency,
                    amount,
                )

                sender_account.balance -= amount
                recipient_account.balance += converted_amount

                sender_account.save()
                recipient_account.save()

                PaymentTransaction.objects.create(
                    sender=request.user,
                    recipient=recipient,
                    amount_sent=amount,
                    sender_currency=sender_account.currency,
                    amount_received=converted_amount,
                    recipient_currency=recipient_account.currency,
                    exchange_rate=rate,
                    transaction_type="DIRECT",
                )

                Notification.objects.create(
                    user=recipient,
                    message=f"You received {converted_amount} {recipient_account.currency} from {request.user.username}.",
                )

                Notification.objects.create(
                    user=request.user,
                    message=f"You sent {amount} {sender_account.currency} to {recipient.username}.",
                )

                send_mail(
                    subject="Payment received",
                    message=f"You received {converted_amount} {recipient_account.currency} from {request.user.email}.",
                    from_email=None,
                    recipient_list=[recipient.email],
                    fail_silently=True,
                )

                send_mail(
                    subject="Payment sent",
                    message=f"You sent {amount} {sender_account.currency} to {recipient.email}.",
                    from_email=None,
                    recipient_list=[request.user.email],
                    fail_silently=True,
                )

            messages.success(request, "Payment sent successfully.")
            return redirect("transactions_history")
    else:
        form = DirectPaymentForm()

    return render(request, "payapp/send_payment.html", {"form": form})

@login_required
def request_payment(request):
    if request.method == "POST":
        form = PaymentRequestForm(request.POST)

        if form.is_valid():
            target_email = form.cleaned_data["target_email"]
            amount = form.cleaned_data["amount"]

            if request.user.email == target_email:
                messages.error(request, "You cannot request money from yourself.")
                return render(request, "payapp/request_payment.html", {"form": form})

            try:
                target_user = User.objects.get(email=target_email)
            except User.DoesNotExist:
                messages.error(request, "Requested user does not exist.")
                return render(request, "payapp/request_payment.html", {"form": form})

            requester_account = Account.objects.get(user=request.user)

            payment_request = PaymentRequest.objects.create(
                requester=request.user,
                target_user=target_user,
                amount=amount,
                currency=requester_account.currency,
                status="PENDING",
            )

            Notification.objects.create(
                user=target_user,
                message=f"{request.user.email} requested {amount} {requester_account.currency} from you.",
            )

            send_mail(
                subject="Payment request received",
                message=f"{request.user.email} requested {amount} {requester_account.currency} from you.",
                from_email=None,
                recipient_list=[target_user.email],
                fail_silently=True,
            )

            messages.success(request, "Payment request sent successfully.")
            return redirect("transactions_history")
    else:
        form = PaymentRequestForm()

    return render(request, "payapp/request_payment.html", {"form": form})

@login_required
def accept_request(request, request_id):
    payment_request = get_object_or_404(PaymentRequest, id=request_id, target_user=request.user, status="PENDING")

    with transaction.atomic():
        requester = payment_request.requester
        payer = payment_request.target_user

        payer_account = Account.objects.select_for_update().get(user=payer)
        requester_account = Account.objects.select_for_update().get(user=requester)

        rate, converted_amount = convert_currency(
            payer_account.currency,
            requester_account.currency,
            payment_request.amount,
        )

        if payer_account.balance < payment_request.amount:
            messages.error(request, "Insufficient funds to accept this request.")
            return redirect("transactions_history")

        payer_account.balance -= payment_request.amount
        requester_account.balance += converted_amount

        payer_account.save()
        requester_account.save()

        PaymentTransaction.objects.create(
            sender=payer,
            recipient=requester,
            amount_sent=payment_request.amount,
            sender_currency=payer_account.currency,
            amount_received=converted_amount,
            recipient_currency=requester_account.currency,
            exchange_rate=rate,
            transaction_type="REQUEST",
        )

        payment_request.status = "ACCEPTED"
        payment_request.responded_at = timezone.now()
        payment_request.save()

        Notification.objects.create(
            user=requester,
            message=f"{payer.email} accepted your request and paid {converted_amount} {requester_account.currency}.",
        )

        Notification.objects.create(
            user=payer,
            message=f"You accepted a payment request from {requester.email}.",
        )

        send_mail(
            subject="Payment request accepted",
            message=f"{payer.email} accepted your request and paid {converted_amount} {requester_account.currency}.",
            from_email=None,
            recipient_list=[requester.email],
            fail_silently=True,
        )

        send_mail(
            subject="Payment request payment sent",
            message=f"You accepted a payment request from {requester.email}.",
            from_email=None,
            recipient_list=[payer.email],
            fail_silently=True,
        )

    messages.success(request, "Payment request accepted.")
    return redirect("transactions_history")


@login_required
def reject_request(request, request_id):
    payment_request = get_object_or_404(PaymentRequest, id=request_id, target_user=request.user, status="PENDING")
    payment_request.status = "REJECTED"
    payment_request.responded_at = timezone.now()
    payment_request.save()

    Notification.objects.create(
        user=payment_request.requester,
        message=f"{request.user.email} rejected your payment request.",
    )

    send_mail(
        subject="Payment request rejected",
        message=f"{request.user.email} rejected your payment request.",
        from_email=None,
        recipient_list=[payment_request.requester.email],
        fail_silently=True,
    )

    messages.success(request, "Payment request rejected.")
    return redirect("transactions_history")


@login_required
def transactions_history(request):
    search_query = request.GET.get("search", "")
    transaction_filter = request.GET.get("type", "all")
    status_filter = request.GET.get("status", "all")

    sent_transactions = PaymentTransaction.objects.filter(sender=request.user).order_by("-created_at")
    received_transactions = PaymentTransaction.objects.filter(recipient=request.user).order_by("-created_at")
    requests_made = PaymentRequest.objects.filter(requester=request.user).order_by("-created_at")
    requests_received = PaymentRequest.objects.filter(target_user=request.user).order_by("-created_at")

    if search_query:
        sent_transactions = sent_transactions.filter(recipient__email__icontains=search_query)
        received_transactions = received_transactions.filter(sender__email__icontains=search_query)
        requests_made = requests_made.filter(target_user__email__icontains=search_query)
        requests_received = requests_received.filter(requester__email__icontains=search_query)

    if status_filter != "all":
        requests_made = requests_made.filter(status=status_filter)
        requests_received = requests_received.filter(status=status_filter)

    context = {
        "sent_transactions": sent_transactions,
        "received_transactions": received_transactions,
        "requests_made": requests_made,
        "requests_received": requests_received,
        "search_query": search_query,
        "transaction_filter": transaction_filter,
        "status_filter": status_filter,
    }

    return render(request, "payapp/transactions.html", context)


@staff_member_required
def admin_dashboard(request):
    return render(request, "payapp/admin_dashboard.html")

@staff_member_required
def admin_accounts(request):
    accounts = Account.objects.select_related("user").order_by("user__username")
    return render(request, "payapp/admin_accounts.html", {"accounts": accounts})


@staff_member_required
def admin_transactions(request):
    transactions = PaymentTransaction.objects.select_related("sender", "recipient").order_by("-created_at")
    requests = PaymentRequest.objects.select_related("requester", "target_user").order_by("-created_at")

    context = {
        "transactions": transactions,
        "requests": requests,
    }
    return render(request, "payapp/admin_transactions.html", context)


@staff_member_required
def create_admin(request):
    if request.method == "POST":
        form = CreateAdminForm(request.POST)

        if form.is_valid():
            admin_user = form.save(commit=False)
            admin_user.first_name = form.cleaned_data["first_name"]
            admin_user.last_name = form.cleaned_data["last_name"]
            admin_user.email = form.cleaned_data["email"]
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()

            messages.success(request, "Administrator created successfully.")
            return redirect("admin_dashboard")
        else:
            messages.error(request, "Could not create administrator. Please correct the errors below.")
    else:
        form = CreateAdminForm()

    return render(request, "payapp/create_admin.html", {"form": form})

@login_required
def profile(request):
    account = Account.objects.get(user=request.user)

    context = {
        "account": account,
    }

    return render(request, "payapp/profile.html", context)

@staff_member_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if user == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect("admin_accounts")
    user.delete()
    messages.success(request, "User deleted successfully.")

    return redirect("admin_accounts")