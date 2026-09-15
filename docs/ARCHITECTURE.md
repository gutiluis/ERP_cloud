## Frontend API Layer

The frontend API layer provides the communication boundary between
React UI components and the Flask backend API.

### Checkout API

`frontend/src/api/checkout.js` encapsulates HTTP communication with
the checkout endpoints.

```text
Checkout UI
    ↓
frontend/src/api/checkout.js
    ↓ HTTP
Flask Checkout API
    ↓
Checkout / Order / Payment logic
    ↓
Stripe
```
