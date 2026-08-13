import requests
from langchain_core.tools import tool


@tool
def currency_converter(amount: float, from_currency: str, to_currency: str) -> str:
    """
    Convert an amount from one currency to another using an external API.
    """

    # Validate amount
    if amount <= 0:
        return "Error: Amount must be greater than 0."

    # Validate currency codes
    from_currency = from_currency.upper().strip()
    to_currency = to_currency.upper().strip()

    if len(from_currency) != 3 or len(to_currency) != 3:
        return "Error: Currency codes must be 3 letters, such as USD or INR."

    try:
        url = (
            f"https://api.frankfurter.app/latest"
            f"?amount={amount}"
            f"&from={from_currency}"
            f"&to={to_currency}"
        )

        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return "Error: Currency API request failed."

        data = response.json()

        if "rates" not in data or to_currency not in data["rates"]:
            return f"Error: Unable to convert {from_currency} to {to_currency}."

        converted_amount = data["rates"][to_currency]

        return (
            f"{amount} {from_currency} = "
            f"{converted_amount} {to_currency}"
        )

    except requests.exceptions.Timeout:
        return "Error: Currency API request timed out."

    except requests.exceptions.RequestException:
        return "Error: Unable to connect to the currency API."

    except Exception as e:
        return f"Error: Unexpected error occurred: {str(e)}"