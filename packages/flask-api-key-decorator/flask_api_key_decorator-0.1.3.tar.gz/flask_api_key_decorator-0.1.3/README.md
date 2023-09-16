# Flask API Key Decorator

A simple decorator for requiring an API key in order to access flask endpoints or methods.

It checks for an API key and adds the requirement to the swagger documentation.

## Installation

```bash
pip install flask-api-key-decorator
```

## Usage

Import the library

```
from require_api_key import require_api_key
```

Use it to decorate your Flask routes:

```python
@app.route('/')
@require_api_key
def home():
    return "Hello, World!"
```

By default, the decorator looks for the API key in the 'x-api-key' header. If you want to use a different header, you can specify it using the header_name parameter:

```python
@app.route('/')
@require_api_key(header_name='custom-header')
def home():
    return "Hello, World!"
```

## Setting the API key

The API key can be set in two ways:

1. As an environment variable named `API_KEY`
2. As an argument to the decorator

```python
@app.route('/')
@require_api_key(key='your-api-key')
def home():
    return "Hello, World!"
```

To set multiple API keys, separate them with a comma.

```bash
export API_KEY=your-api-key-1,your-api-key-2
```

## License

MIT (see [LICENSE.md](LICENSE.md)
