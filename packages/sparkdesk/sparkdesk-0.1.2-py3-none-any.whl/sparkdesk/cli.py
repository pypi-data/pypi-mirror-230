import click

from sparkdesk.authentication import Authentication
from sparkdesk.chat import Chat


@click.command()
@click.option("--app-id", required=True)
@click.option("--api-secret", required=True)
@click.option("--api-key", required=True)
def _chat(app_id: str, api_secret: str, api_key: str):
    authentication = Authentication(
        api_key=api_key, api_secret=api_secret, api_version="v1.1"
    )
    chat = Chat(authentication, app_id)
    print("-----------------------")
    print("q: 退出会话")
    print("reset: 清除会话上下文")
    print("-----------------------")
    while True:
        question = input("Ask: ")
        if question in {"q", "quit", "exit", "stop"}:
            break
        if question == "reset":
            chat.reset_chat_context()
        responses = chat.ask(question)
        for response in responses:
            for content in [
                e["content"] for e in response["payload"]["choices"]["text"]
            ]:
                print(content, end="")
        print("\n")


if __name__ == "__main__":
    _chat()
