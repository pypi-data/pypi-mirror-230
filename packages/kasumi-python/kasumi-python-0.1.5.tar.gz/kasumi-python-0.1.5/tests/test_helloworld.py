from typing import List, Dict
from kasumi import Kasumi,KasumiConfigration,DefaultSearchStrategy
from examples.helloworld.helloworld import PopipaSpider,popipa_search_desc

def test_helloworld():
    token = input("Please input your token: ")
    app = Kasumi(
        KasumiConfigration(app_id=0, token=0, search_key="",search_desc=popipa_search_desc, search_strategy=DefaultSearchStrategy)
    )
    app.add_spider(PopipaSpider(app))
    app.run_forever()