# Created by: Ausar686
# https://github.com/Ausar686

from typing import Union
from collections import deque

import tiktoken

from .base_actor import BaseActor
from ..chat import Message


class TokenCounter(BaseActor):
    _tokens_per_message = 3
    _models = [
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k",
        "gpt-4",
        "gpt-4-32k",
    ]
    
    def __init__(self, model: str="gpt-3.5-turbo"):
        super().__init__(model)
        self.encodings = {key: tiktoken.encoding_for_model(key) for key in self._models}
        return

    @property
    def encoding(self):
        return self.encodings[self.model]
    
    def run(self, obj: Union[str, dict, list, None]) -> int:
        if obj is None:
            return 0
        if isinstance(obj, str):
            return self.count_from_str(obj)
        elif isinstance(obj, dict):
            return self.count_from_dict(obj)
        elif isinstance(obj, list):
            return self.count_from_list(obj)
        elif isinstance(obj, deque):
            # Counting for list and deque are the same
            return self.count_from_list(obj)
        elif isinstance(obj, Message):
            # Counting for Message is equal to counting from dict
            return self.count_from_dict(obj.to_openai())
        else:
            raise TypeError(f"Parameter 'obj' must be str, dict, list, deque, Message or None, not {type(obj)}.")
            
    def count_from_str(self, string: str) -> int:
        return len(self.encoding.encode(string))
    
    def count_from_dict(self, dct: dict) -> int:
        # Here we assume, that a message is provided in OpenAI dict form:
        # {"role": role, "content": content}
        # So we simply call 'count_from_str' on content
        return self.count_from_str(dct.get("content"))
    
    def count_from_list(self, lst: list) -> int:
        # Here we assume that a list of messages in OpenAI dict form is given:
        # [{"role": role, "content": content}, ...]
        # So we simply iterate over the list and call 'count_from_dict'
        num_tokens = 0
        for message in lst:
            num_tokens += self._tokens_per_message
            num_tokens += self.count_from_dict(message)
        num_tokens += 3 # every reply is primed with <|start|>assistant<|message|>
        return num_tokens