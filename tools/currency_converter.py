from langchain_core.tools import tool
import requests


@tool
def currency_converter(
    amount: float,
    from_currency: str,
    to_currency: str
) -> str:
    """
    Convert an amount from one currency to another.
    Uses an external API when available, with a fallback rate for demo use.
    """

    if amount <= 0:
        return "Error: Amount must be greater than 0."

    from_currency = from_currency.upper().strip()
    to_currency = to_currency.upper().strip()

    if len(from_currency) != 3 or len(to_currency) != 3:
        return "Error: Currency codes must be 3 letters, such as USD or INR."

    # Try external API first
    try:
        url = (
            f"https://api.frankfurter.app/latest"
            f"?amount={amount}"
            f"&from={from_currency}"
            f"&to={to_currency}"
        )

        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()

            if "rates" in data and to_currency in data["rates"]:
                converted_amount = data["rates"][to_currency]

                return (
                    f"{amount} {from_currency} = "
                    f"{converted_amount} {to_currency}"
                )

    except requests.exceptions.RequestException:
        pass

    # Fallback rate for reliable demonstration
    fallback_rates = {
        ("USD", "INR"): 83.0,
        ("INR", "USD"): 1 / 83.0
    }

    key = (from_currency, to_currency)

    if key in fallback_rates:
        converted_amount = amount * fallback_rates[key]

        return (
            f"{amount} {from_currency} = "
            f"{round(converted_amount, 2)} {to_currency} "
            f"(demo fallback rate)"
        )

    return (
        f"Error: Unable to convert {from_currency} to "
        f"{to_currency} because the currency API is unavailable."
    )