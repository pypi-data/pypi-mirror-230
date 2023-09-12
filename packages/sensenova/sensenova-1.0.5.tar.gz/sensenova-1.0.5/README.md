# Sensenova Python Library

The Sensenova Python library provides convenient access to the Sensenova API from applications written in the Python
language.

## Installation

You don't need this source code unless you want to modify the package. If you just
want to use the package, just run:

```sh
pip install --upgrade sensenova
```


## Usage

### Configure API KEY

Set environment variable:

```shell
export SENSENOVA_ACCESS_KEY_ID=
export SENSENOVA_SECRET_ACCESS_KEY=
```

Or set sensenova.access_key_id and sensenova.secret_access_key to its value:

```python
import sensenova

sensenova.access_key_id = "..."
sensenova.secret_access_key = "..."
```

### API

#### cli

```shell
sensenova api chat_completions.create -m xxx -g user "Say this is a test!" --stream
```

#### python

```python
import sensenova

# create a chat completion
chat_completion = sensenova.ChatCompletion.create(
    model="xxx",
    messages=[{"role": "user", "content": "Say this is a test!"}]
)

# print the chat completion
print(chat_completion.data.choices[0].message)
```

#### python async

Async support is available in the API by prepending a to a network-bound method:

```python
import sensenova
import asyncio


async def create_chat_completion():
    chat_completion_resp = await sensenova.ChatCompletion.acreate(
        model="xxx",
        messages=[{"role": "user", "content": "Say this is a test!"}]
    )
    print(chat_completion_resp.data.choices[0].message)


asyncio.run(create_chat_completion())
```

To make async requests more efficient, you can pass in your own aiohttp.ClientSession, but you must manually close the
client session at the end of your program/event loop:

```python
import sensenova
from aiohttp import ClientSession

sensenova.aiosession.set(ClientSession())
# At the end of your program, close the http session
await sensenova.aiosession.get().close()
```

### Tools

Run the following command on data.json to get the cleaned_data.json file

```sh
sensenova tools fine_tunes.prepare_data -f data.json
```

## Requirements

- Python 3.7.1+