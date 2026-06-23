from decimal import Decimal
from django.conf import settings
from django.db import models


class Account(models.Model):
    CURRENCY_CHOICES = [
        ("GBP", "British Pound"),
        ("USD", "US Dollar"),
        ("EUR", "Euro"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.currency} {self.balance}"


class PaymentTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ("DIRECT", "Direct Payment"),
        ("REQUEST", "Payment Request Fulfilled"),
    ]

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_payments",
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_payments",
    )
    amount_sent = models.DecimalField(max_digits=12, decimal_places=2)
    sender_currency = models.CharField(max_length=3)
    amount_received = models.DecimalField(max_digits=12, decimal_places=2)
    recipient_currency = models.CharField(max_length=3)
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=6)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} -> {self.recipient.username} ({self.amount_sent} {self.sender_currency})"


class PaymentRequest(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("ACCEPTED", "Accepted"),
        ("REJECTED", "Rejected"),
    ]

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="requests_made",
    )
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="requests_received",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.requester.username} requested {self.amount} {self.currency} from {self.target_user.username}"


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "Read" if self.is_read else "Unread"
        return f"{self.user.username}: {self.message} ({status})"