"""
Manage GPT LLM (Casual language modeling completion tasks)
    to make the query more reliable and trackable
"""


import json
import logging
import os
from typing import Optional


class OpenAIComplete:
    """
    OpenAI Complete wrapper
    A handler to call LLM completion model

    We might have other LLM completion models in the future,
        if there're other providers
    """
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "davinci-text-002",
        model_max_tokens: int = 4095,
    ):
        if api_key is None:
            api_key = os.environ.get('OPENAI_API_KEY')
        if api_key is None:
            raise KeyError(
                "Please set up OPENAI_API_KEY"
            )
        # we import these packages here to avoid
        # import error when we don't have openai
        try:
            import openai
            from transformers import AutoTokenizer
        except ImportError as e:
            logging.error(
                "Please install openai and transformers"
            )
            raise e
        self.openai = openai
        self.openai.api_key = api_key
        self.tokenizer = AutoTokenizer.from_pretrained(
            "gpt2"
        )
        self.model = model
        self.model_max_tokens = model_max_tokens

    def cap_tokens(
        self, text: str,
        ask_max_tokens: int = 3090,
    ) -> str:
        """
        Cap the number of tokens in the text
        To avoid the model from generating too long text
        """
        tokens = self.tokenizer.tokenize(text)
        if len(tokens) > ask_max_tokens:
            return self.tokenizer.convert_tokens_to_string(
                tokens[-ask_max_tokens:])
        return text

    def log_io(self, prompt: str, reply: str, **kwargs):
        """
        Log the input and output of the model API
            Feel free to overwrite this function while inheriting
        """
        logging.info(
            json.dumps(
                dict(
                    prompt=prompt,
                    reply=reply,
                    **kwargs
                )
            )
        )

    def __call__(self, prompt: str, **kwargs):
        # if answer's max_tokens is set,
        # we need to cap the prompt
        if "max_tokens" in kwargs:
            prompt = self.cap_tokens(
                prompt,
                self.model_max_tokens - kwargs["max_tokens"])
        reply = self.openai.Completion(
            prompt,
            **kwargs
        ).choices[0].text
        self.log_io(prompt, reply, **kwargs)
        return reply
