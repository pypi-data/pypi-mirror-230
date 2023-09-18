# gpt-trim

This is a (slightly) faster version of [KillianLucas/tokentrim](https://pypi.org/project/tokentrim) for longer message arrays.

In average, gpt-trim is \~80% faster than tokentrim, and that tokentrim is around 5x\~7x slower.

Although gpt-trim is fast, I still need to finish my LeetCode problems that I left years ago, just so that I can make it 20x faster than 95% of people.

## Usage

The usage is quite similiar to `tokentrim`.

```python
import gpt_trim

trimmed = gpt_trim.trim(
    messages, 
    model="gpt-3.5-turbo"
)
print(trimmed)
```

Alternatively, you can assign the token limit manually:

```python
gpt_trim.trim(
    messages,
    max_tokens=100
)
```

You can also add system messages with ease:

```python
import gpt_trim

messages = [
    ..., # long, long content
    {
        "role": "user",
        "content": "It's about drive, it's about power"
    }
]
trimmed = gpt_trim.advanced_trim(
    messages,
    system_messages=[
        {
            "role": "system",
            "content": "You'll act like the celebrity: The Rock."
        }
    ],
    model="gpt-3.5-turbo",
)
print(trimmed)
```

The catch? It's slower. With great power comes great... patience.

## Comparison

You can compare this project to [KillianLucas/tokentrim](https://pypi.org/project/tokentrim) like so:

```python
import time

import gpt_trim
import tiktoken
import tokentrim

pattern = "d!3h.l7$fj" # 10 tokens
messages = [
    {
        "role": "user",
        "content": pattern * 5000 # 50000 tokens
    }
]

# cache first
enc = tiktoken.get_encoding("cl100k_base")
gpt_trim.num_tokens_from_messages(
    messages,
    enc
)

def test(provider):
    print("Testing", provider.__name__)

    s = time.time()
    result = provider.trim(
        messages,
        model="gpt-3.5-turbo",
    )

    print(f"took {(time.time() - s):.4f}s\n")

# Swap the following for every test and see tokentrim 
# struggles when dealing with longer context.
test(gpt_trim)
test(tokentrim)
```

***

Right. I was bored.
