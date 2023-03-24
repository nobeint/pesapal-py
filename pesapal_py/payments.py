import json
import requests


class PesaPal(object):
    def __init__(self, consumer_key, consumer_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.base_production_url = "https://pay.pesapal.com/v3/api"
        self.base_demo_url = "https://cybqa.pesapal.com/pesapalv3/api"
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def authenticate(self) -> dict:
        """
        Authenticates against PesaPal

        returns:
            status (str): success or failed (always returned)
            error (str): error message from pesapal when authentication fails (returned only when status is failed)
            message (str): a brief description about the response received (returned only when status is failed)
            token (str): Bearer token to authenticate all other PesaPal APIs (returned only when status is success)
            expiry (str): Date and time the token will expire. The access token usually expires after 5mins - UTC (returned only when status is success)

        Explore https://developer.pesapal.com/how-to-integrate/e-commerce/api-30-json/authentication for more details
        """
        auth_payload = {
            "consumer_key": self.consumer_key,
            "consumer_secret": self.consumer_secret,
        }
        auth_response = requests.post(
            f"{self.base_production_url}/Auth/RequestToken",
            json.dumps(auth_payload),
            headers=self.headers,
        )
        if auth_response.status_code == 200:
            auth_data = json.loads(auth_response.content)
            if auth_data["status"] == "200":
                return {
                    "status": "success",
                    "token": auth_data["token"],
                    "expiry": auth_data["expiryDate"],
                }
            else:
                return {
                    "status": "failed",
                    "error": auth_data["error"]["code"],
                    "message": auth_data["error"]["message"],
                }
        return {
            "status": "failed",
            "error": auth_response.status_code,
            "message": f"invalid server response",
        }

    def register_ipn(self, token: str, ipn_url: str) -> dict:
        """
        Registers an Instant Payment Notification (IPN) URL on PesaPal servers.
        This registered IPN URL is used by By PesaPal to send payment notifications

        params:
            token (str): active token from the `authenticate` method
            ipn_url (str): the URL that PesaPal will use to send payment notifications

        returns:
            status (str): success or failed (always returned)
            error (str): error message when registering ipn fails (returned only when status is failed)
            message (str): a brief description about the response received (returned only when status is failed)
            ipn_url (str): the successfully registered ipn url
            ipn_id (str): unique identifier that's liked to the IPN endpoint URL (GUID)

        Explore https://developer.pesapal.com/how-to-integrate/e-commerce/api-30-json/registeripnurl for more details
        """
        register_ipn_payload = {"url": ipn_url, "ipn_notification_type": "POST"}
        self.headers["Authorization"] = f"Bearer {token}"
        register_ipn_response = requests.post(
            f"{self.base_production_url}/URLSetup/RegisterIPN",
            json.dumps(register_ipn_payload),
            headers=self.headers,
        )
        if register_ipn_response.status_code == 200:
            ipn_data = json.loads(register_ipn_response.content)
            if ipn_data["status"] == "200":
                return {
                    "status": "success",
                    "ipn_url": ipn_data["url"],
                    "ipn_id": ipn_data["ipn_id"],
                }
            return {
                "status": "failed",
                "error": ipn_data["error"]["code"],
                "message": ipn_data["error"]["message"],
            }

        return {
            "status": "failed",
            "error": register_ipn_response.status_code,
            "message": f"invalid server response",
        }

    def transact(
        self,
        token: str,
        description: str,
        transaction_id: str,
        amount: int,
        callback_url: str,
        ipn_id: str,
        email_address: str,
        phone_number: str,
        country_code: str,
        first_name: str,
        last_name: str,
        currency: str = "KES",
    ) -> dict:
        """
        Performs a PesaPal transaction with the provided parameters on the PesaPal servers

        params:
            token (str): active token from the `authenticate` method
            description (str): description of the transaction (maximum 100 characters)
            transaction_id (str): unique transaction identifier generated by your system (maximum 50 characters)
            amount (float): amount to transact
            callback_url (str): a valid URL which Pesapal will redirect your clients to after processing the payment (e.g. https://<your-site>.com/pending-transaction)
            ipn_id (str): represents the IPN URL which Pesapal will send notifications to after payments have been processed, generated by the `register_ipn` method
            email_address (str): optional if phone number is provided, mandatory if phone number is NOT provided
            phone_number (str): optional if email address is provided, mandatory if email address is NOT provided
            country_code (str) [Optional]: 2 characters long country code in [ISO 3166-1]
            first_name [Optional]: customer's first name
            last_name [Optional]: customer's last name
            currency: the currency you want to charge your customers (ISO Currency Codes)

        returns:
            status (str): success or failed (always returned)
            error (int): error message when authentication fails (returned only when status is failed)
            message (str): a brief description about the response received (returned only when status is failed)
            order_tracking_id (str): unique order id generated by Pesapal.
            merchant_reference (str): transaction_id from your system that was part of the params of this method
            redirect_url (str): URL generated that contains the payment instructions. Redirect to this URL or load it within an iframe
        """
        transaction_payload = {
            "id": transaction_id,
            "currency": currency,
            "amount": amount,
            "description": description,
            "callback_url": callback_url,
            "notification_id": ipn_id,
            "billing_address": {
                "email_address": email_address,
                "phone_number": phone_number,
                "country_code": country_code,
                "first_name": first_name,
                "last_name": last_name,
            },
        }
        self.headers["Authorization"] = f"Bearer {token}"
        transact_response = requests.post(
            f"{self.base_production_url}/Transactions/SubmitOrderRequest",
            json.dumps(transaction_payload),
            headers=self.headers,
        )
        if transact_response.status_code == 200:
            transaction_data = json.loads(transact_response.content)
            if transaction_data["status"] == "200":
                return {
                    "status": "success",
                    "order_tracking_id": transaction_data["order_tracking_id"],
                    "merchant_reference": transaction_data["merchant_reference"],
                    "redirect_url": transaction_data["redirect_url"],
                }

            return {
                "status": "failed",
                "error": transaction_data["error"]["code"],
                "message": transaction_data["error"]["message"],
            }

        return {
            "status": "failed",
            "error": transact_response.status_code,
            "message": f"invalid server response",
        }

    def get_transaction_status(self, token: str, order_tracking_id: str) -> dict:
        """
        Gets the status of a PesaPal transaction using the order tracking id returned during `transact`

        params:
            token (str): active token from the `authenticate` method
            order_tracking_id (str): unique order id generated by Pesapal during `transact`

        returns:
            status (str): success, pending or failed (always returned)
            error (str): error code when getting transaction status fails
            message (str): a brief description about the response received (returned only when status is failed)
        """
        self.headers["Authorization"] = f"Bearer {token}"
        get_transaction_status_response = requests.get(
            f"{self.base_production_url}/Transactions/GetTransactionStatus?orderTrackingId={order_tracking_id}",
            headers=self.headers,
        )

        if get_transaction_status_response.status_code == 200:
            transaction_status_data = json.loads(
                get_transaction_status_response.content
            )
            if transaction_status_data["status"] == "200":
                if transaction_status_data["payment_status_description"] == "Completed":
                    return {
                        "status": "success",
                        "error": 12,
                        "message": "transaction successful",
                    }
                elif transaction_status_data["payment_status_description"] == "Pending":
                    return {
                        "status": "pending",
                        "error": 12,
                        "message": "transaction pending",
                    }
                else:
                    return {
                        "status": "failed",
                        "error": transaction_status_data["error"]["code"],
                        "message": "transaction failed",
                    }

            return {
                "status": "failed",
                "error": transaction_status_data["error"]["code"],
                "message": transaction_status_data["error"]["message"],
            }
        transaction_status_data = json.loads(get_transaction_status_response.content)
        error_message = json.loads(transaction_status_data["message"])
        return {
            "status": "unknown",
            "error": get_transaction_status_response.status_code,
            "message": error_message["error"]["message"],
        }
