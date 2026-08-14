import requests

def convert_currency(amount: float, from_currency: str, to_currency: str):
    source = from_currency.upper().strip()
    target = to_currency.upper().strip()

    if amount < 0:
        raise ValueError("Amount cannot be negative.")
    if len(source) != 3 or len(target) != 3:
        raise ValueError("Currency codes must use 3 letters, such as USD and INR.")
    if source == target:
        return {"amount": amount, "from": source, "to": target, "rate": 1.0, "converted": amount}

    url = f"https://api.frankfurter.app/latest?amount={amount}&from={source}&to={target}"
    try:
        response = requests.get(url, timeout=8)
        response.raise_for_status()
        value = response.json()["rates"][target]
        return {"amount": amount, "from": source, "to": target,
                "rate": value / amount if amount else 0, "converted": value}
    except requests.RequestException as exc:
        raise RuntimeError("Currency service is temporarily unavailable.") from exc
    except (KeyError, TypeError):
        raise RuntimeError("Currency service returned an unexpected response.")
