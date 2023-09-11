from kasumi import KasumiEmbedding, Kasumi, KasumiConfigration, DefaultSearchStrategy
import sys

def test_embedding():
    token = input("Please input your token: ")

    app = Kasumi(
        KasumiConfigration(
            app_id=0,
            token=token,
            search_key="",
            search_strategy=DefaultSearchStrategy
        )
    )

    embedding = app.embeding_text("我是傻比")
    print(embedding)