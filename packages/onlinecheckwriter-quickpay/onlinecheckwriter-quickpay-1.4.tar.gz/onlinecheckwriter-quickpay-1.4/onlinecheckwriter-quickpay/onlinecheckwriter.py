import requests
import json

class OnlineCheckWriter:
    SANDBOX_BASE_URL = 'https://test.onlinecheckwriter.com/api/v3'
    LIVE_BASE_URL = 'https://app.onlinecheckwriter.com/api/v3'

    def __init__(self, token="", environment="SANDBOX"):
        self.token = token
        self.base_url = self.SANDBOX_BASE_URL if environment == "SANDBOX" else self.LIVE_BASE_URL

    def set_token(self, token):
        self.token = token

    def set_environment(self, environment):
        if environment == "SANDBOX":
            self.base_url = self.SANDBOX_BASE_URL
        elif environment == "LIVE":
            self.base_url = self.LIVE_BASE_URL

    def send_request(self, resource_url, data, request_method="POST"):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        
        url = f"{self.base_url}/{resource_url}"
        
        try:
            response = requests.request(request_method, url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "completed": 0,
                "errorMsg": str(e)
            }



    def send_check(self, data):
        return self.send_request("quickpay/check", data)

    def send_echeck(self, data):
        return self.send_request("quickpay/echeck", data)

    def send_mailcheck(self, data):
        return self.send_request("quickpay/mailcheck", data)

    def send_direct_deposit(self, data):
        return self.send_request("quickpay/directdeposit", data)

    def send_virtual_card(self, data):
        return self.send_request("quickpay/virtualcard", data)

    def send_wire(self, data):
        return self.send_request("quickpay/wire", data)