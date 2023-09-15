# Caddy Python Wrapper

A Python package that provides a simple wrapper around the Caddy Tool API.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Initialization](#initialization)
  - [Making Requests](#making-requests)
  - [Searching Tools](#searching-tools)
- [Documentation](#documentation)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Installation

To install the package, run:

```bash
pip install caddy-python
```

## Usage

### Initialization

First, import the package and initialize it with your API key.

```python
from caddy import Tools

tools = Tools(api_key="your-api-key-here")
```

### Making Proxy Requests

To make a proxy request based on the returned values from the OpenAI client function call:

```python
response = tools.request(method="POST", path="function_name", body="function_args")
```

### Searching Tools

To search for tools based on a query:

```python
items = tools.search_tools(query="your-query-here")
```

## How It Works

The `caddy-python` package interacts with the Caddy API to provide two main functionalities:

1. **Function Selection**: Helps OpenAI clients to select the most relevant functions for their needs.
2. **Proxy Execution**: Uses the `request` method to act as a proxy for executing the selected functions.

Putting it all together:
```python
from caddy import Tools

import json
import openai


openai.api_key = "your-openai-api-key-here"

user_message = "User prompt here"


messages = [
    {
        "role": "system",
        "content": "System prompt here"
    },
    {
        "role": "user",
        "content": user_message
    }
]

tools = Tools(api_key="your-caddy-api-key-here") # API key optional

completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=messages,
    function=tools.search_tools(query=user_message)
)

if completion.choices[0].finish_reason == 'function_call':
    function_name = completion.choices[0]['message']['function_call']['name']
    function_args = json.loads(completion.choices[0]['message']['function_call']['arguments'])
    
    response = tools.request(
        method="POST",
        path=function_name,
        body=function_args
    )
    
    messages.append({
        "role": "function",
        "name": function_name,
        "content": str(response)
    })
    
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    
messages.append({
    "role": "assistant",
    "content": completion.choices[0].message.content
})
    
print(messages)
```
## Testing

To run the tests:

```bash
python -m unittest tests/test_api.py
```

## Contributing

1. Fork the repository.
2. Create your feature branch (\`git checkout -b feature/fooBar\`).
3. Commit your changes (\`git commit -am 'Add some fooBar'\`).
4. Push to the branch (\`git push origin feature/fooBar\`).
5. Create a new Pull Request.