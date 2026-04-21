# freemobile-sms

Python client for the [Free Mobile SMS API](https://mobile.free.fr/). Send SMS notifications to your Free Mobile phone programmatically.

## Installation

```bash
pip install freemobile-sms
```

## Quick Start

### Environment Variables

```bash
export FREE_MOBILE_USER=12345678      # Your Free Mobile customer ID
export FREE_MOBILE_PASSWORD=yourApiKey # Your API key (from your Free Mobile account)
```

### Python (Programmatic)

```python
from freemobile_sms import FreeMobileClient

# Uses FREE_MOBILE_USER / FREE_MOBILE_PASSWORD from environment
with FreeMobileClient() as client:
    result = client.send("Server alert: disk usage at 90%")
    print(result.ok)       # True
    print(result.message)   # "SMS sent successfully"
```

Or with explicit credentials:

```python
from freemobile_sms import FreeMobileClient, FreeMobileSettings

settings = FreeMobileSettings(user="12345678", password="yourApiKey")
with FreeMobileClient(settings=settings) as client:
    result = client.send("Hello from Python!")
```

### Async Python

```python
from freemobile_sms import AsyncFreeMobileClient

async with AsyncFreeMobileClient() as client:
    result = await client.send("Async alert!")
    print(result.message)
```

### CLI

```bash
# Using environment variables
freemobile-sms send "Hello from the command line!"

# Using options
freemobile-sms send "Hello!" --user 12345678 --password yourApiKey
```

## API Reference

### `FreeMobileClient`

Synchronous client. Use as a context manager for automatic cleanup.

| Method | Description |
|--------|-------------|
| `send(message)` | Send an SMS. Returns `SMSResult`. |

### `AsyncFreeMobileClient`

Asynchronous client. Same interface, but `send()` is `async`.

### `FreeMobileSettings`

Pydantic Settings model. Reads from environment variables with `FREE_MOBILE_` prefix, or from a `.env` file.

| Field | Env var | Default |
|-------|---------|---------|
| `user` | `FREE_MOBILE_USER` | `""` |
| `password` | `FREE_MOBILE_PASSWORD` | `""` |
| `api_url` | `FREE_MOBILE_API_URL` | `https://smsapi.free-mobile.fr/sendmsg` |

### `SMSResult`

| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | Whether the SMS was sent |
| `status_code` | `int` | HTTP status code from the API |
| `message` | `str` | Human-readable description |
| `ok` | `bool` | Alias for `success` |

### Exceptions

| Exception | Status | Description |
|-----------|--------|-------------|
| `FreeMobileClientError` | — | Base exception |
| `AuthenticationError` | 402 | Invalid credentials |
| `AccountBlockedError` | 403 | Account blocked from notifications |
| `ServerError` | 500 | Free Mobile server error |

## Development

```bash
# Install with dev dependencies
uv pip install -e ".[dev]"

# Run tests with coverage (requires 100%)
pytest

# Lint and format
ruff check .
ruff format .

# Install pre-commit hooks
pre-commit install
```

## License

MIT