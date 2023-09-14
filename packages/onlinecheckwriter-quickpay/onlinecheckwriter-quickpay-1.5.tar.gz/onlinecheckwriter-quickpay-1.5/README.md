---
Onlinecheckwriter Quick Pay Api
---

Streamlined Payment API with Multi-Channel Support: Seamlessly Integrate Checks, eChecks, Virtual Cards, ACH/Direct Deposits, and Wire Transfers into Your Application

Full API documenation [source](https://apiv3.onlinecheckwriter.com/) to see how it works.


## Sample Code

````
from onlinecheckwriter_quickpay.onlinecheckwriter import OnlineCheckWriter

# Initialize the OnlineCheckWriter instance with your API token and environment
ocw = OnlineCheckWriter()
ocw.set_token("YOUR_API_TOKEN")
ocw.set_environment("SANDBOX")  # or "LIVE" if needed

# Prepare the data for a payment (example data)
data = {
    "source": {"accountType": "bankaccount", "accountId": ""},
    "destination": {
        "name": "John Myres",
        "company": "Tyler Payment Technologist",
        "address1": "5007 richmond rd",
        "address2": "",
        "city": "Tyler",
        "state": "TX",
        "zip": "75701",
        "phone": "9032457713",
        "email": "support@onlinecheckwriter.com",
    },
    "payment_details": {
        "amount": 500,
        "memo": "for game",
        "note": "Note For Internal Purpose",
    },
}

# Test sending a check payment
result = ocw.send_check(data)

# Print the result
print(result)
````

Available method
result = ocw.send_check(data)

result = ocw.send_mailcheck(data)

result = ocw.send_direct_deposit(data)

result = ocw.send_virtual_card(data)

result = ocw.send_wire(data)

