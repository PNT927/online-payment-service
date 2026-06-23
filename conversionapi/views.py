from decimal import Decimal, InvalidOperation
from django.http import JsonResponse


RATES = {
    "GBP": {"GBP": Decimal("1.00"), "USD": Decimal("1.25"), "EUR": Decimal("1.15")},
    "USD": {"GBP": Decimal("0.80"), "USD": Decimal("1.00"), "EUR": Decimal("0.92")},
    "EUR": {"GBP": Decimal("0.87"), "USD": Decimal("1.09"), "EUR": Decimal("1.00")},
}


def conversion(request, currency1, currency2, amount_of_currency1):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET is supported."}, status=405)

    currency1 = currency1.upper()
    currency2 = currency2.upper()

    if currency1 not in RATES or currency2 not in RATES[currency1]:
        return JsonResponse({"error": "Unsupported currency."}, status=400)

    try:
        amount = Decimal(amount_of_currency1)
    except InvalidOperation:
        return JsonResponse({"error": "Invalid amount."}, status=400)

    rate = RATES[currency1][currency2]
    converted_amount = (amount * rate).quantize(Decimal("0.01"))

    return JsonResponse(
        {
            "from_currency": currency1,
            "to_currency": currency2,
            "rate": str(rate),
            "converted_amount": str(converted_amount),
        },
        status=200,
    )