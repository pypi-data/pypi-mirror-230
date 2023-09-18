"""The core of gpt-trim."""

from typing import Dict, List, Literal, Optional, Tuple

import tiktoken

# source:
# https://github.com/KillianLucas/tokentrim/blob/main/tokentrim/tokentrim.py
MODEL_MAX_TOKENS = {
    'gpt-4': 8192,
    'gpt-4-0613': 8192,
    'gpt-4-32k': 32768,
    'gpt-4-32k-0613': 32768,
    'gpt-3.5-turbo': 4096,
    'gpt-3.5-turbo-16k': 16384,
    'gpt-3.5-turbo-0613': 4096,
    'gpt-3.5-turbo-16k-0613': 16384,
}

ModelSelector = Optional[
    Literal[
        "gpt-4",
        "gpt-4-0613",
        "gpt-4-32k",
        "gpt-4-32k-0613",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k",
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-13k-0613",
    ]
]

Messages = List[Dict[str, str]]


def num_tokens_from_messages(
    messages, 
    encoding: tiktoken.Encoding
) -> Tuple[List[List[int]], List[int]]:
    """Returns the number of tokens used by a list of messages."""

    num_tokens = []
    tokens = []

    for message in messages:
        cur = 4
        # every message follows <im_start>{role/name}\n{content}<im_end>\n

        for key, value in message.items():
            encoded = encoding.encode(value)

            if key == "content":
                tokens.append(encoded)
            
            cur += len(encoded)

            if key == "name":
                cur -= 1  # role is always required and always 1 token

        num_tokens.append(cur)

    #num_tokens += 2  # every reply is primed with <im_start>assistant

    return tokens, num_tokens


def basic_trim(
    msgs: Messages,
    sys_toks: int,
    enc: tiktoken.Encoding,
    MAX_TOKENS: int = 4096
) -> Messages:
    """Basic trimming.
    
    It's not recommended to use this unless you know what the terrifying and 
        unfathomable code in this project is doing.

    Otherwise, use ``trim()`` instead.

    Args:
        msgs (list of dict of str: str): List of messages.
        sys_toks (str): System message(s) token length.
        enc (:obj:`tiktoken.Encoding`): Encoding.
        MAX_TOKENS (int, optional): Max tokens. Default 4096.
    """
    
    dots = [1131] if enc.name == "cl100k_base" else enc.encode('...')

    max_tokens = MAX_TOKENS - 2 - len(dots) - sys_toks

    if max_tokens < 1:
        raise ValueError(
            "Max token is negative. Usually caused by:\n"
            "- System message tokens ~= max tokens\n"
            "- Max tokens < 0"
        )

    messages = msgs.copy()
    # <im_start>assistant & '...'
    
    tokens, n_tokens_list = num_tokens_from_messages(messages, enc)
    n_tokens = sum(n_tokens_list)
    
    if n_tokens > max_tokens:
        current_n_tokens = n_tokens
    
        for index in range(len(msgs)):
            if current_n_tokens > max_tokens:
                to_trim = current_n_tokens - max_tokens
        
                if to_trim > n_tokens_list[index]:
                    messages[index] = {}
                    current_n_tokens -= n_tokens_list[index]
    
                else:
                    messages[index]['content'] = "..." + enc.decode(
                        tokens[index][to_trim:]
                    )
                    current_n_tokens -= to_trim
            else:
                return messages

    return messages

def advanced_trim(
    messages: Messages,
    *,
    system_messages: Messages,
    model: ModelSelector = "gpt-3.5-turbo",
    max_tokens: Optional[int] = None,
    encoding: str = "cl100k_base",
):
    """Advanced trimming with system messages as arrays.

    Args:
        messages (list of dict of str: str): Messages.
        system_messages (list of dict of str: str): System messages.
        model (:obj:`ModelSelector`, optional): The model. Default ``gpt-3.5-turbo``.
        max_tokens (int, optional): Alternatively, set a token limit.
        encoding (str): Encoding. Default ``cl100k_base``.
    """
    enc = tiktoken.get_encoding(encoding)
    sys_toks = sum(
        num_tokens_from_messages(system_messages, enc)[1]
    ) if system_messages else 0

    trimmed = basic_trim(
        messages,
        sys_toks,
        enc,
        MODEL_MAX_TOKENS.get(model, max_tokens) # type: ignore
    )

    if not system_messages:
        return trimmed[trimmed.count({}):]

    return system_messages + trimmed[trimmed.count({}):]


def trim(
    messages: Messages,
    *,
    model: ModelSelector = "gpt-3.5-turbo",
    max_tokens: Optional[int] = None,
    encoding: str = "cl100k_base"
) -> Messages:
    """Trims message arrays to fit the "max token" limit.

    Args:
        messages (list of dict of str: str): Messages.
        model (:obj:`ModelSelector`, optional): The model. Default ``gpt-3.5-turbo``.
        max_tokens (int, optional): Alternatively, set a token limit.
        encoding (str): Encoding. Default ``cl100k_base``.
    """

    trimmed = basic_trim(
        messages,
        0,
        tiktoken.get_encoding(encoding),
        MODEL_MAX_TOKENS.get(model, max_tokens) # type: ignore
    )

    return trimmed
