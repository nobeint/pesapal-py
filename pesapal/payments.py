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
                    "error": auth_data["error"],
                    "message": auth_data["error"]["message"],
                }
        return {
            "status": "failed",
            "error": f"invalid HTTP status {auth_response.status_code}",
            "message": f"invalid server response",
        }

    def register_ipn(self, token: str, ipn_url: str) -> dict:
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
                "error": ipn_data["error"],
                "message": ipn_data["error"]["message"],
            }

        return {
            "status": "failed",
            "error": f"invalid HTTP status {register_ipn_response.status_code}",
            "message": f"invalid server response",
        }

    def transact(
        self,
        token: str,
        description: str,
        transaction_id: str,
        amount: int,
        callback_url: str,
        notification_id: str,
        email_address: str,
        phone_number: str,
        country_code: str,
        first_name: str,
        last_name: str,
        currency: str = "KES",
    ) -> dict:
        transaction_payload = {
            "id": transaction_id,
            "currency": currency,
            "amount": amount,
            "description": description,
            "callback_url": callback_url,
            "notification_id": notification_id,
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
                "error": transaction_data["error"],
                "message": transaction_data["error"]["message"],
            }

        return {
            "status": "failed",
            "error": f"invalid HTTP status {transact_response.status_code}",
            "message": f"invalid server response",
        }

    def get_transaction_status(self, token: str, order_tracking_id: str) -> dict:
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
                        "error": {},
                        "message": "transaction successful",
                    }
                elif transaction_status_data["payment_status_description"] == "Pending":
                    return {
                        "status": "pending",
                        "error": {},
                        "message": "transaction pending",
                    }
                else:
                    return {
                        "status": "failed",
                        "error": transaction_status_data["message"],
                        "message": "transaction failed",
                    }

            return {
                "status": "failed",
                "error": transaction_status_data["error"],
                "message": transaction_status_data["error"]["message"],
            }
        transaction_status_data = json.loads(get_transaction_status_response.content)
        error_message = json.loads(transaction_status_data["message"])
        return {
            "status": "unknown",
            "error": f"invalid HTTP status {get_transaction_status_response.status_code}",
            "message": error_message["error"]["message"],
        }
