import requests

# Where USD is the base currency you want to use
url = 'https://v6.exchangerate-api.com/v6/cf8a28d496d7fca12eccfbbc/latest/USD'

# Making our request
response = requests.get(url)
data = response.json()

# Your JSON object
# print(data)
# Function to get the conversion rate for a selected currency
def convert_currency(amount, from_currency, to_currency):
    # Get the base conversion rate from USD
    from_rate = data['conversion_rates'].get(from_currency, 1)
    to_rate = data['conversion_rates'].get(to_currency, 1)
    
    # Convert to USD first, then to the target currency
    usd_amount = amount / from_rate
    converted_amount = usd_amount * to_rate
    return converted_amount

# Input: Amount, from currency, and to currency
def exchange():
    amount = float(input("Enter the amount you want to convert: "))
    from_currency = input("Enter the base currency (e.g., USD, EUR, INR): ").upper()
    to_currency = input("Enter the target currency (e.g., USD, EUR, INR): ").upper()

    converted_amount = convert_currency(amount, from_currency, to_currency)
    print(f"{amount} {from_currency} is equal to {converted_amount:.2f} {to_currency}")

# Run the exchange function
if __name__ == "__main__":
    exchange()