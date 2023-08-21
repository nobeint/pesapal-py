# pesapal-py
A minimalist python library that integrates with PesaPal's API 3.0 - JSON APIs (https://developer.pesapal.com/how-to-integrate/e-commerce/api-30-json/api-reference).

This library abstracts PesaPals API 3.0 into four main methods, `authenticate`, `register_ipn`, `transact` and `get_transaction_status`

## Getting started

### Register as a merchant
1. Register as a PesaPal merchant at https://www.pesapal.com/
2. On successfull registration, you will receive a consumer key and consumer secret via email - keep these safe as they are your API credentials

### Install pesapal-py
```
pip install pesapal-py
```

### Authenticating
```
from pesapal.payments import PesaPal

pesapal = PesaPal("test_consumer_key", "test_consumer_secret")
auth = pesapal.authenticate()
print(auth)
```
This step returns a bearer token that is used with all the other methods below. The token expires after every 5 minutes. To prevent calling this method every time you need to transact, I recommend that you store it in an in-memory data store (e.g. redis) and expire it before 5 minutes.

### Register IPN
```
register_ipn = pesapal.register_ipn("sample_token", "https://www.sample-url.com/ipn")
print(register_ipn)
```

### Transact
```
transact = pesapal.transact(
    token="sample_token",
    description="sample_description",
    transaction_id="sample_transaction_id",
    amount=1000,
    callback_url="https://www.callback-url.com/status",
    ipn_id="sample_ipn_id",
    email_address="sample@email-address.com",
    phone_number="254722001122",
    country_code="KE",
    first_name="first",
    last_name="last",
    currency="KES",
)
print(transact)
```

### Validate Transaction
```
transaction_status = pesapal.get_transaction_status(
    token="sample_token", order_tracking_id="sample_order_tracking_id"
)
print(transaction_status)
```
