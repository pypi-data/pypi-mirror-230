from typing import Dict, List

from sparkdesk.consts import MAX_REQUEST_TOKENS_COUNT


def count_tokens(text: str) -> int:
    """
    Count the number of tokens in a text.

    A token is approximately equal to 1.5 Chinese characters or 0.8 English words.

    Args:
        text (str): The input text.

    Returns:
        int: The number of tokens in the text.
    """
    return len(text.encode("utf-8", errors="ignore")) // 2


def limit_chat_history(
    chat_history: List[Dict[str, str]],
    max_request_tokens_count: int = MAX_REQUEST_TOKENS_COUNT,
) -> List[Dict[str, str]]:
    """
    Limits the chat history by removing messages that exceed
    the maximum number of request tokens count.
    """
    total_count = 0
    new_chat_history: List[Dict[str, str]] = []
    for message in reversed(chat_history):
        content = message["content"]
        total_count += count_tokens(content)
        if total_count > MAX_REQUEST_TOKENS_COUNT:
            remain_tokens = total_count - max_request_tokens_count
            message["content"] = (content.encode("utf-8")[:remain_tokens]).decode(
                "utf-8", errors="ignore"
            )
            new_chat_history.insert(0, message)
            break
        new_chat_history.insert(0, message)
    return new_chat_history
