# Klaviyo Python Library

[![pypi](https://img.shields.io/pypi/v/fern-klaviyo.svg)](https://pypi.python.org/pypi/fern-klaviyo)
[![fern shield](https://img.shields.io/badge/%F0%9F%8C%BF-SDK%20generated%20by%20Fern-brightgreen)](https://github.com/fern-api/fern)

## Installation

Add this dependency to your project's build file:

```bash
pip install fern-klaviyo
# or
poetry add fern-klaviyo
```

## Usage

```python
from klaviyo.client import Klaviyo

klaviyo_client = Klaviyo(
  api_key="YOUR_API_KEY"
)
response = klaviyo_client.profiles.get_profile_relationships_lists('01GDDKASAP8TKDDA2GRZDSVP4H')

print(f"Received response from klaviyo: {response}");
```

## Async Client

```python
from klaviyo.client import AsyncKlaviyo

import asyncio

klaviyo_client = AsyncKlaviyo(
  api_key="YOUR_API_KEY"
)

async def create_environment() -> None:
    response = klaviyo_client.profiles.get_profile_relationships_lists('01GDDKASAP8TKDDA2GRZDSVP4H')
    print(f"Received response from klaviyo: {response}");

asyncio.run(create_environment())
```

## Timeouts
By default, the client is configured to have a timeout of 60 seconds. You can customize this value at client instantiation. 

```python
from klaviyo.client import Klaviyo

klaviyo_client = Klaviyo(
  api_key="YOUR_API_KEY",
  timeout=15
)
```

## Handling Exceptions
All exceptions thrown by the SDK will sublcass [ApiError](./src/klaviyo/core/api_error.py). 

```python
from klaviyo.client import Klaviyo
from klaviyo.core import ApiError

try:
  klaviyo_client.profiles.get_profile_relationships_lists('01GDDKASAP8TKDDA2GRZDSVP4H')
except APIError as e:  
  # handle any api related error
```

## Beta status

This SDK is in beta, and there may be breaking changes between versions without a major version update. Therefore, we recommend pinning the package version to a specific version in your pyproject.toml file. This way, you can install the same version each time without breaking changes unless you are intentionally looking for the latest version.

## Contributing

While we value open-source contributions to this SDK, this library is generated programmatically. Additions made directly to this library would have to be moved over to our generation code, otherwise they would be overwritten upon the next generated release. Feel free to open a PR as a proof of concept, but know that we will not be able to merge it as-is. We suggest opening an issue first to discuss with us!

On the other hand, contributions to the README are always very welcome!
