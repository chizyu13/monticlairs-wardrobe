# your_app/utils/mobile_money.py
import requests
from django.conf import settings

class MobileMoney:
    def __init__(self):
        # MTN MoMo credentials (add these to settings.py)
        self.mtn_api_user = settings.MTN_API_USER
        self.mtn_api_key = settings.MTN_API_KEY
        self.mtn_subscription_key = settings.MTN_SUBSCRIPTION_KEY
        self.mtn_base_url = "https://sandbox.mtn.com"  # Replace with production URL later

        # Airtel Money credentials
        self.airtel_client_id = settings.AIRTEL_CLIENT_ID
        self.airtel_client_secret = settings.AIRTEL_CLIENT_SECRET
        self.airtel_base_url = "https://openapiuat.airtel.africa"  # Replace with production URL later

    # Get MTN MoMo access token
    def get_mtn_token(self):
        url = f"{self.mtn_base_url}/token/"
        headers = {
            "Authorization": f"Basic {self.mtn_api_user}:{self.mtn_api_key}",
            "Ocp-Apim-Subscription-Key": self.mtn_subscription_key
        }
        response = requests.post(url, headers=headers)
        return response.json().get("access_token") if response.status_code == 200 else None

    # Request payment via MTN MoMo
    def mtn_request_payment(self, amount, phone_number, external_id):
        token = self.get_mtn_token()
        if not token:
            return {"success": False, "message": "Failed to authenticate with MTN"}

        url = f"{self.mtn_base_url}/collection/v1_0/requesttopay"
        headers = {
            "Authorization": f"Bearer {token}",
            "Ocp-Apim-Subscription-Key": self.mtn_subscription_key,
            "X-Reference-Id": external_id,
            "X-Target-Environment": "sandbox",  # Change to "production" later
            "Content-Type": "application/json"
        }
        payload = {
            "amount": str(amount),
            "currency": "ZMW",  # Adjust currency based on your region (e.g., UGX, ZMW)
            "externalId": external_id,
            "payer": {"partyIdType": "MSISDN", "partyId": phone_number},
            "payerMessage": "Payment for Montclair Wardrobe",
            "payeeNote": "Order payment"
        }
        response = requests.post(url, json=payload, headers=headers)
        return {"success": response.status_code == 202, "transaction_id": external_id}

    # Get Airtel Money access token
    def get_airtel_token(self):
        url = f"{self.airtel_base_url}/auth/oauth2/token"
        payload = {
            "client_id": self.airtel_client_id,
            "client_secret": self.airtel_client_secret,
            "grant_type": "client_credentials"
        }
        response = requests.post(url, data=payload)
        return response.json().get("access_token") if response.status_code == 200 else None

    # Request payment via Airtel Money
    def airtel_request_payment(self, amount, phone_number, external_id):
        token = self.get_airtel_token()
        if not token:
            return {"success": False, "message": "Failed to authenticate with Airtel"}

        url = f"{self.airtel_base_url}/merchant/v1/payments/request-payment"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "amount": str(amount),
            "currency": "ZMW",  # Adjust currency
            "msisdn": phone_number,
            "reference": external_id,
            "description": "Payment for Montclair Wardrobe"
        }
        response = requests.post(url, json=payload, headers=headers)
        return {"success": response.status_code == 200, "transaction_id": external_id}