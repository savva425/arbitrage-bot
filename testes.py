
import json
import requests


trades_buy = json.loads(requests.get("https://www.htx.com" + f"/-/x/otc/v1/data/trade-market?coinId=1&currency=11&tradeType=sell&currPage=1&payMethod=29&acceptOrder=0&country=&blockType=general&online=1&range=0&amount=&isThumbsUp=false&isMerchant=false&isTraded=false&onlyTradable=false&isFollowed=false").text)


print(trades_buy["data"][0]["maxTradeLimit"], trades_buy["data"][0]["price"])

# надо в 

# for el in ["USDT", "BTC", "ETH", "USDC"]:
#     print(el)
#     ENDURL = "https://api2.bybit.com"
#     payload = {"userId":el,"tokenId":"USDT","currencyId":"RUB","payment":["582"],"side":"1","size":"5","page":"1","amount":"","authMaker":"false","canTrade":"false"}

#     trades_buy = json.loads(requests.post(url=(ENDURL + "/fiat/otc/item/online"), data=payload).text)

#     print(trades_buy["result"]["items"][0]["price"])

#     print("sell -------------")

#     payload = {"userId":"","tokenId":el,"currencyId":"RUB","payment":["582"],"side":"0","size":"5","page":"1","amount":"","authMaker":"false","canTrade":"false"}

#     trades_sell = json.loads(requests.post(url=(ENDURL + "/fiat/otc/item/online"), data=payload).text)

#     print(trades_sell["result"]["items"][0]["price"])


"""
ENDURL = "https://www.htx.com"

symbols_all_pairs_p2p = set(
    ("RUB", "USDT"),
    ("RUB", "BTC"),
    ("RUB", "USDD"),
    ("RUB", "HTX"),
    ("RUB", "TRX"),
    ("RUB", "ETH"),
    ("RUB", "EOS"),
    ("RUB", "XRP"),
    ("RUB", "LTC"),
)


coinIds = [
    2, #USDT
    1, #BTC
    62, #USDD
    65, #HTX
    22, #TRX
    3, #ETH
    5, #EOS
    7, #XRP
    8, #LTC
]

for coinId in coinIds:
    trades_buy = json.loads(requests.get(ENDURL + f"/-/x/otc/v1/data/trade-market?coinId={coinId}&currency=11&tradeType=sell&currPage=1&payMethod=29&acceptOrder=0&country=&blockType=general&online=1&range=0&amount=&isThumbsUp=false&isMerchant=false&isTraded=false&onlyTradable=false&isFollowed=false").text)
    trades_sell = json.loads(requests.get(ENDURL + f"/-/x/otc/v1/data/trade-market?coinId={coinId}&currency=11&tradeType=buy&currPage=1&payMethod=&acceptOrder=-1&country=&blockType=general&online=1&range=0&amount=&isThumbsUp=false&isMerchant=false&isTraded=false&onlyTradable=false&isFollowed=false").text)
    print("buy -----------------" + str(coinId))
    for el in trades_buy["data"]:
        print(el["price"], el["minTradeLimit"], el["maxTradeLimit"], ENDURL + f"/en-us/fiat-crypto/trader/{el['uid']}")

    print("sell ----------------" + str(coinId))

    for el in trades_sell["data"]:
        print(el["price"], el["minTradeLimit"], el["maxTradeLimit"], ENDURL + f"/en-us/fiat-crypto/trader/{el['uid']}")

    print("---------------------" + str(coinId))

"""