from pybit import spot

from arbitrage_libs import exchange
import time

session = spot.HTTP(
    endpoint='https://api.bybit.com', 
    api_key='9moZh8QjNSEPtqqmNk',
    api_secret='eiPv6Vu4OgDxINoFRu04d8QW6hwf7fUXgjJm'
)

#@dev посмотерь и попробовать как работает ордерная торговля и как отследить, что сделка
bybit = exchange.Bybit(session)
def wait_order(active_order_info):
    last_order = (session.get_active_order()["result"][0])

    start = time.time()
    while int(session.get_active_order()["result"][0]["orderId"]) != int(active_order_info["result"]["orderId"]):
        last_order = (session.get_active_order()["result"][0])
        # if start - time.time() > 100:
        #     return -666

    last_order = (session.get_active_order()["result"][0])


    # важдные поля last_order["executedQty"] и last_order["cummulativeQuoteQty"]
    return last_order


def place_order(side, symbol, from_t, price):
    qty = 0
    info_from_symbol = bybit.session.best_bid_ask_price(symbol=symbol)

    for el in session.query_account_info()["result"]["loanAccountList"]:
        if el["tokenId"] == from_t:
            qty = float(el["free"])
    
    if from_t != symbol[:len(from_t)]:
        qty = qty/price

    print(qty)
    for i in range(20):
        last_order = {}
        if i == 0:
            try:
                active_order_info = session.place_active_order(
                    symbol=symbol,
                    side=side,
                    type="LIMIT",
                    qty=qty,
                    price=price,
                    timeInForce="GTC"
                )
                last_order = wait_order(active_order_info)
                if last_order == -666:
                    #@dev необходимо отменить ордер и продать по цене маркета и в wait_order тоже поправить
                    session.cancel_active_order(
                        orderId=active_order_info["result"]["orderId"]
                    )
                    # info_from_symbol = bybit.session.best_bid_ask_price(symbol=symbol)
                    # if from_t != "USDT":
                    #     price_err = float(info_from_symbol["result"]["bidPrice"])
                    #     session.place_active_order(
                    #         symbol=from_t+"USDT",
                    #         side=side,
                    #         type="LIMIT",
                    #         qty=qty,
                    #         price=price_err,
                    #         timeInForce="GTC"
                    #     )
                    # return -666
                break
            except:
                continue
        else:
            try:
                active_order_info = session.place_active_order(
                    symbol=symbol,
                    side=side,
                    type="LIMIT",
                    qty=str(qty)[:-i],
                    price=price,
                    timeInForce="GTC"
                )
                last_order = wait_order(active_order_info)
                if last_order == -666:
                    session.cancel_active_order(
                        orderId=active_order_info["result"]["orderId"]
                    )
                    # info_from_symbol = bybit.session.best_bid_ask_price(symbol=symbol)
                    # if from_t != "USDT":
                    #     price_err = float(info_from_symbol["result"]["bidPrice"])
                    #     session.place_active_order(
                    #         symbol=from_t+"USDT",
                    #         side=side,
                    #         type="LIMIT",
                    #         qty=qty,
                    #         price=price_err,
                    #         timeInForce="GTC"
                    #     )
                    # return -666
                break
            except:
                continue


    # важдные поля last_order["executedQty"] и last_order["cummulativeQuoteQty"]
    return last_order
info_from_symbol = bybit.session.best_bid_ask_price(symbol="ETHUSDT")
price = float(info_from_symbol["result"]["askPrice"])
print(price)

active_order_info = place_order("BUY", "ETHUSDT", "USDT", price)

print(active_order_info)

info_from_symbol = bybit.session.best_bid_ask_price(symbol="ETHUSDT")
price = float(info_from_symbol["result"]["bidPrice"])

active_order_info = place_order("SELL", "ETHUSDT", "ETH", price)

print(active_order_info)



