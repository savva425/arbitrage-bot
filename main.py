from collections import defaultdict 

import threading
from queue import Queue

import time

import math
from pybit import spot
import requests
from arbitrage_libs import exchange, graph


#@dev must be in class exchanged or add global variable session
def wait_order(active_order_info):
    last_order = (session.get_active_order()["result"][0])

    while int(session.get_active_order()["result"][0]["orderId"]) != int(active_order_info["result"]["orderId"]):
        last_order = (session.get_active_order()["result"][0])

    last_order = (session.get_active_order()["result"][0])


    # важдные поля last_order["executedQty"] и last_order["cummulativeQuoteQty"]
    return last_order

def place_order(side, symbol, from_t):
    qty = 0
    for el in session.query_account_info()["result"]["loanAccountList"]:
        if el["tokenId"] == from_t:
            qty = float(el["free"])
    for i in range(15):
        last_order = {}
        if i == 0:
            try:
                active_order_info = (session.place_active_order(
                    symbol=symbol,
                    side=side,
                    type="MARKET",
                    qty=qty,
                    timeInForce="GTC"
                ))
                last_order = wait_order(active_order_info)
                break
            except:
                continue
        else:
            try:
                active_order_info = (session.place_active_order(
                    symbol=symbol,
                    side=side,
                    type="MARKET",
                    qty=str(qty)[:-i],
                    timeInForce="GTC"
                ))
                last_order = wait_order(active_order_info)
                break
            except:
                continue


    # важдные поля last_order["executedQty"] и last_order["cummulativeQuoteQty"]
    return last_order

if __name__ == "__main__":
    while True:
        session = spot.HTTP(
            endpoint='https://api.bybit.com', 
            api_key='9moZh8QjNSEPtqqmNk',
            api_secret='eiPv6Vu4OgDxINoFRu04d8QW6hwf7fUXgjJm'
        )
        bybit = exchange.Bybit(session)
        bybit.get_info_from_sybmol.cache_info()
        bybit.get_info_from_sybmol.cache_clear()

        dict_id_sumbol = {}
        dict_sumbol_id = {}
        start_top = 0
        for i, from_token in enumerate(bybit.get_all_token_name()):
            dict_id_sumbol[from_token] = i
            dict_sumbol_id[i] = from_token
            if from_token == "USDT":
                start_top = i

        g = graph.Graph(len(bybit.get_all_token_name()))

        def created_graph(q):
            while q.empty() == False:
                from_token = q.get()
                #print(from_token, end=" - ")
                for to_token in bybit.get_all_tokens()[from_token].get_all_token_pairs():
                    # предположил что нужно поменять to и from тк мы вычесляем немного иначе
                    # короче мы же вычесляем самую выгодную сделку, а она по алгоритму получается самой наооборот невыгодной то есть по курсу который
                    # в конце мы должны купить а не продать, перечитать еше раз алгоритм арбитража
                    #print(dict_id_sumbol[from_token], dict_id_sumbol[to_token], bybit.get_price_token_pair(from_token, to_token), end=" ")
                    g.addEdge(dict_id_sumbol[from_token], dict_id_sumbol[to_token], math.log(bybit.get_price_token_pair(from_token, to_token)))
                #print()

                q.task_done()

        q = Queue()
        for el in bybit.get_all_token_name():
            q.put(el)

        thread1 = threading.Thread(target=created_graph, args=(q,), daemon=True)
        thread2 = threading.Thread(target=created_graph, args=(q,), daemon=True)
        thread3 = threading.Thread(target=created_graph, args=(q,), daemon=True)
        thread4 = threading.Thread(target=created_graph, args=(q,), daemon=True)

        thread1.start()
        thread2.start()
        thread3.start()
        thread4.start()
        q.join()


        g.BellmanFord(start_top)

        tmp = g.getPred(start_top)
        #print(dict_sumbol_id[start_top], start_top)
        tmp_pre_last = 0
        tmp_last = 0

        path_trade = [(dict_sumbol_id[start_top], start_top)]
        print("in while")

        start_time = time.time()
        flag_timeout_err = False
        while tmp != start_top:
            if time.time() - start_time > 10:
                flag_timeout_err = True
                break
            if tmp == tmp_pre_last:
                break
            path_trade.append((dict_sumbol_id[tmp], tmp))
            tmp_pre_last = tmp_last
            tmp_last = tmp
            tmp = g.getPred(tmp)

        if flag_timeout_err:
            continue

        path_trade.append((dict_sumbol_id[start_top], start_top))

        #print(path_trade)

        path_trade_price = []
        for i in range(len(path_trade) - 1):
            from_t = path_trade[i]
            to_t   = path_trade[i + 1]

            if to_t == from_t:
                del path_trade[i]
                continue
            

            price = bybit.get_absolute_token_price(from_t[0], to_t[0])

            path_trade_price.append((from_t, to_t, bybit.get_correct_symbol(from_t[0], to_t[0]), price))
            #print(from_t, to_t, bybit.get_correct_symbol(from_t[0], to_t[0]), price)

        money = 1000
        for from_t, to_t, symbol, _ in path_trade_price:
            price = bybit.get_absolute_token_price(from_t[0], to_t[0])
            print(from_t, to_t, price)
            if from_t[0] == symbol[:len(from_t[0])]:
                money = money * price
            else:
                money = money / price
        print(money)

        if money > 1005:
            for from_t, to_t, symbol, price in path_trade_price:
                if from_t[0] == symbol[:len(from_t[0])]:
                    order = place_order("SELL", symbol, from_t[0])
                else:
                    order = place_order("BUY", symbol, from_t[0])
                print(order)


        # изменить чтобы получал цену покупки для одного и цену продажи именно для биржи для подсчета самих путей 
        # хотя вроде ничего не изменилось и выводит странные сделки разобраться с этим

        # можно изменить и оставить то что есть и искать сделки с стандартным обменным курсом типо last_trade а потом просто среди них искать прибыльную


        path_trade_price = path_trade_price[::-1]
        money = 1000
        for to_t, from_t, symbol, _ in path_trade_price:
            price = bybit.get_absolute_token_price(from_t[0], to_t[0])
            print(from_t, to_t, price)
            if from_t[0] == symbol[:len(from_t[0])]:
                money = money * price
            else:
                money = money / price
        print(money)

    # if money >= 500:
    # 	money = 500
    # 	for to_t, from_t, symbol, _ in path_trade_price:
    # 		price = bybit.get_absolute_token_price(from_t[0], to_t[0])
    # 		if from_t[0] == symbol[:len(from_t[0])]:
    # 			order = place_order("SELL", money)
    # 			money = order["cummulativeQuoteQty"]
    # 		else:
    # 			order = place_order("BUY", money)
    # 			money = order["executedQty"]




    # This code is contributed by Neelam Yadav 

    # dai eth usdt
    # 1803 1820

    # еще раз попробовать заупстить добавил кеширование при получение цен на токены
