try:
    import unittest2 as unittest
except ImportError:
    import unittest

import mock
import json

from pesapal_py.payments import PesaPal


class TestPesapal(unittest.TestCase):
    def setUp(self):
        self.pesapal = PesaPal("test_consumer_key", "test_consumer_secret")

    def test_authentication_successful(self):
        with mock.patch("requests.post") as mocked_post:
            mocked_post.return_value.status_code = 200
            mocked_post.return_value.content = json.dumps(
                {
                    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYa",
                    "expiryDate": "2021-08-26T12:29:30.5177702Z",
                    "error": "",
                    "status": "200",
                    "message": "Request processed successfully",
                }
            )
            actual_auth_request = self.pesapal.authenticate()
            self.assertEqual(actual_auth_request["status"], "success")
            self.assertIsNotNone(actual_auth_request["token"])

    def test_authentication_not_successful(self):
        with mock.patch("requests.post") as mocked_post:
            mocked_post.return_value.status_code = 200
            mocked_post.return_value.content = json.dumps(
                {
                    "error": {
                        "error_type": "api_error",
                        "code": "invalid_consumer_key_or_secret_provided",
                        "message": "",
                    },
                    "status": "failed",
                    "message": "Request not processed successfully",
                }
            )
            actual_auth_request = self.pesapal.authenticate()
            self.assertEqual(actual_auth_request["status"], "failed")
            self.assertIsNotNone(actual_auth_request["error"])

    def test_register_ipn_successful(self):
        with mock.patch("requests.post") as mocked_post:
            mocked_post.return_value.status_code = 200
            mocked_post.return_value.content = json.dumps(
                {
                    "url": "https://www.myapplication.com/ipn",
                    "created_date": "2022-03-03T17:29:03.7208266Z",
                    "ipn_id": "e32182ca-0983-4fa0-91bc-c3bb813ba750",
                    "status": "200",
                }
            )
            actual_register_ipn_request = self.pesapal.register_ipn(
                "test_token", "https://test_url"
            )
            self.assertEqual(actual_register_ipn_request["status"], "success")
            self.assertIsNotNone(actual_register_ipn_request["ipn_url"])

    def test_register_ipn_not_successful(self):
        with mock.patch("requests.post") as mocked_post:
            mocked_post.return_value.status_code = 200
            mocked_post.return_value.content = json.dumps(
                {
                    "error": {
                        "error_type": "api_error",
                        "code": "some error code",
                        "message": "some error message",
                    },
                    "status": "failed",
                    "message": "Request not processed successfully",
                }
            )
            actual_register_ipn_request = self.pesapal.register_ipn(
                "test_token", "https://test_url"
            )
            self.assertEqual(actual_register_ipn_request["status"], "failed")
            self.assertIsNotNone(actual_register_ipn_request["error"])

    def test_transact_successful(self):
        with mock.patch("requests.post") as mocked_post:
            mocked_post.return_value.status_code = 200
            mocked_post.return_value.content = json.dumps(
                {
                    "order_tracking_id": "b945e4af-80a5-4ec1-8706-e03f8332fb04",
                    "merchant_reference": "TEST1515111119",
                    "redirect_url": "https://cybqa.pesapal.com/pesapaliframe/PesapalIframe3/Index/?OrderTrackingId=b945e4af-80a5-4ec1-8706-e03f8332fb04",
                    "status": "200",
                }
            )
            actual_transact_request = self.pesapal.transact(
                "test_token",
                "test payment",
                "GSKKSG",
                1000,
                "https://test_callback_url",
                "test_ipn_id",
                "test@email.com",
                "test_phone_number",
                "KE",
                "first_name",
                "last_name",
            )
            self.assertEqual(actual_transact_request["status"], "success")
            self.assertIsNotNone(actual_transact_request["order_tracking_id"])
            self.assertIsNotNone(actual_transact_request["redirect_url"])

    def test_get_transaction_status_successful(self):
        with mock.patch("requests.get") as mocked_get:
            mocked_get.return_value.status_code = 200
            mocked_get.return_value.content = json.dumps(
                {
                    "payment_method": "Visa",
                    "amount": 100,
                    "created_date": "2022-04-30T07:41:09.763",
                    "confirmation_code": "6513008693186320103009",
                    "payment_status_description": "Success",
                    "description": "Test description",
                    "message": "Request processed successfully",
                    "payment_account": "476173**0010",
                    "call_back_url": "https://test.com/?OrderTrackingId=7e6b62d9-883e-440f-a63e-e1105bbfadc3&OrderMerchantReference=1515111111",
                    "status_code": 2,
                    "merchant_reference": "1515111111",
                    "payment_status_code": "",
                    "currency": "KES",
                    "status": "200",
                    "payment_status_description": "Completed",
                }
            )
            actual_get_transaction_status_request = self.pesapal.get_transaction_status(
                "test_token", "test_order_tracking_id"
            )
            self.assertEqual(
                actual_get_transaction_status_request["status"],
                "success",
            )
            self.assertIsNotNone(actual_get_transaction_status_request["message"])

    def test_get_transaction_status_pending(self):
        with mock.patch("requests.get") as mocked_get:
            mocked_get.return_value.status_code = 200
            mocked_get.return_value.content = json.dumps(
                {
                    "payment_method": "Visa",
                    "amount": 100,
                    "created_date": "2022-04-30T07:41:09.763",
                    "confirmation_code": "6513008693186320103009",
                    "payment_status_description": "Success",
                    "description": "Test description",
                    "message": "Request pending",
                    "payment_account": "476173**0010",
                    "call_back_url": "https://test.com/?OrderTrackingId=7e6b62d9-883e-440f-a63e-e1105bbfadc3&OrderMerchantReference=1515111111",
                    "status_code": 2,
                    "merchant_reference": "1515111111",
                    "payment_status_code": "",
                    "currency": "KES",
                    "status": "200",
                    "payment_status_description": "Pending",
                }
            )
            actual_get_transaction_status_request = self.pesapal.get_transaction_status(
                "test_token", "test_order_tracking_id"
            )
            self.assertEqual(
                actual_get_transaction_status_request["status"],
                "pending",
            )
            self.assertIsNotNone(actual_get_transaction_status_request["message"])

    def test_get_transaction_status_failed(self):
        with mock.patch("requests.get") as mocked_get:
            mocked_get.return_value.status_code = 200
            mocked_get.return_value.content = json.dumps(
                {
                    "payment_method": "Visa",
                    "amount": 100,
                    "created_date": "2022-04-30T07:41:09.763",
                    "confirmation_code": "6513008693186320103009",
                    "payment_status_description": "Success",
                    "description": "Test description",
                    "message": "Request failed",
                    "payment_account": "476173**0010",
                    "call_back_url": "https://test.com/?OrderTrackingId=7e6b62d9-883e-440f-a63e-e1105bbfadc3&OrderMerchantReference=1515111111",
                    "status_code": 2,
                    "merchant_reference": "1515111111",
                    "payment_status_code": "",
                    "currency": "KES",
                    "status": "200",
                    "error": {
                        "error_type": None,
                        "code": 0,
                        "message": "msg",
                        "call_back_url": "",
                    },
                    "payment_status_description": "Failed",
                }
            )
            actual_get_transaction_status_request = self.pesapal.get_transaction_status(
                "test_token", "test_order_tracking_id"
            )
            self.assertEqual(
                actual_get_transaction_status_request["status"],
                "failed",
            )
            self.assertIsNotNone(actual_get_transaction_status_request["message"])
