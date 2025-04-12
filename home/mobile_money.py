class MobileMoney:
    """
    A class to handle mobile money payment requests for MTN and Airtel.
    Currently uses mock responses for testing; extend with real API calls as needed.
    """

    def airtel_request_payment(self, amount, phone_number, external_id):
        """
        Simulate an Airtel Mobile Money payment request.
        
        Args:
            amount (float): The amount to charge.
            phone_number (str): The customer's phone number (e.g., +260971234567).
            external_id (str): A unique identifier for the transaction.
        
        Returns:
            dict: A response with success status and transaction details.
        """
        # Mock response for Airtel payment
        return {
            "success": True,  # Simulate a successful request
            "transaction_id": f"AIRTEL-{external_id}",
            "message": "Airtel payment request sent (mocked)",
            "amount": amount,
            "phone_number": phone_number
        }

    def mtn_request_payment(self, amount, phone_number, external_id):
        """
        Simulate an MTN Mobile Money payment request.
        
        Args:
            amount (float): The amount to charge.
            phone_number (str): The customer's phone number (e.g., +260761234567).
            external_id (str): A unique identifier for the transaction.
        
        Returns:
            dict: A response with success status and transaction details.
        """
        # Mock response for MTN payment (mirrors your original mock in views.py)
        return {
            "success": True,
            "transaction_id": f"MTN-{external_id}",
            "access_token": "mock_token",
            "token_type": "access_token",
            "expires_in": 3600,
            "amount": amount,
            "phone_number": phone_number
        }