from django import forms


class DirectPaymentForm(forms.Form):
    recipient_email = forms.EmailField(label="Recipient email")
    amount = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)

class PaymentRequestForm(forms.Form):
    target_email = forms.EmailField(label="User email to request from")
    amount = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)