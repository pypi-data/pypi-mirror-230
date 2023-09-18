import json
import logging
from typing import Dict, List

from websockets.sync.client import connect

from sparkdesk.authentication import Authentication

logger = logging.getLogger(__name__)


class BaseChatCompletion:
    """
    Class for creating chat completion.
    """

    def __init__(
        self,
        authentication: Authentication,
        app_id: str,
        user_id: str = "default_user",
        domain: str = "general",
        temperature: float = 0.5,
        max_tokens: int = 2048,
    ):
        """
        Constructor for the class.

        Args:
            authentication (Authentication):
                The authentication object used to authenticate the API calls.
            app_id (str):
                The ID of the application.
            user_id (str, optional):
                The ID of the user. Defaults to "default_user".
            domain (str, optional):
                The domain of the user. Defaults to "general".
            temperature (float, optional):
                The temperature to control the randomness of the generated output.
                Defaults to 0.5.
            max_tokens (int, optional):
                The maximum number of tokens to generate. Defaults to 2048.
        """
        self.authentication = authentication
        self.app_id = app_id
        self.user_id = user_id
        self.domain = domain
        self.temperature = temperature
        self.max_tokens = max_tokens

    def _build_ws_input_message(self, message_text: List[Dict[str, str]]):
        return json.dumps(
            {
                "header": {
                    "app_id": self.app_id,
                    "uid": self.user_id,
                },
                "parameter": {
                    "chat": {
                        "domain": self.domain,
                        "temperature": self.temperature,
                        "max_tokens": self.max_tokens,
                    }
                },
                "payload": {"message": {"text": message_text}},
            }
        )

    @staticmethod
    def _process_ws_response_message(response_message: str):
        return json.loads(response_message)


class ChatCompletion(BaseChatCompletion):
    def create(self, message_text: List[Dict[str, str]]):
        """
        Create chat completion.
        reference: https://www.xfyun.cn/doc/spark/Web.html

        Args:
            message_text:
                A list of dictionaries containing the message content.
                The total length of the message content should be less than 8192.
                one token is approximately equal to 1.5 Chinese characters or
                0.8 English words.
                ex: [{"role": "user", "content": "Hi"}]

        Yields:
            An iterator that yields the processed response messages from the websocket.
        """
        with connect(self.authentication.get_authorization_url()) as websocket:
            input_message = self._build_ws_input_message(message_text)
            logger.debug(f"send: {input_message}")
            websocket.send(input_message)

            response_message = websocket.recv()
            logger.debug(f"recv: {response_message}")
            while True:
                processed_ws_response_message = self._process_ws_response_message(
                    response_message
                )
                yield processed_ws_response_message
                # if last message, exit
                if processed_ws_response_message["header"]["status"] == 2:
                    break
                response_message = websocket.recv()
                logger.debug(f"recv: {response_message}")
