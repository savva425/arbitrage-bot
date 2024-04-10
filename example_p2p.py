from arbitrage_libs import exchange
from arbitrage_libs.graph import Graph
from arbitrage_libs.config import MONEY

from pybit import spot

import threading
from queue import Queue
import math

from config import api_key, api_secret

MONEY = 100000
def created_graph(q, fst_exchange, snd_exchange, dict_id_sumbol, g, BLACKLIST):
    while q.empty() == False:
        from_token = q.get()
        if from_token[:-5] not in BLACKLIST:
            if from_token[-5:] == "fstex":
                for to_token in fst_exchange.get_all_tokens()[from_token[:-5]].get_all_token_pairs():
                    try:
                        if fst_exchange.check_token_pair(from_token[:-5], to_token):
                            g.addEdge(dict_id_sumbol[from_token], dict_id_sumbol[to_token + "fstex"], math.log(fst_exchange.get_price_token_pair(from_token[:-5], to_token)))
                    except:
                        print(1)
            else:
                for to_token in snd_exchange.get_all_tokens()[from_token[:-5]].get_all_token_pairs():
                    try:
                        if snd_exchange.check_token_pair(from_token[:-5], to_token):
                            g.addEdge(dict_id_sumbol[from_token], dict_id_sumbol[to_token + "sndex"], math.log(snd_exchange.get_price_token_pair(from_token[:-5], to_token)))
                    except:
                        print(2)
        q.task_done()

def arbitrage_main(fst_exchange, snd_exchange, BLACKLIST):
    while True:		
        print(fst_exchange.get_info_from_sybmol.cache_info())
        fst_exchange.get_info_from_sybmol.cache_clear()
        print(fst_exchange.get_info_from_sybmol.cache_info())

        print(snd_exchange.get_info_from_sybmol.cache_info())
        snd_exchange.get_info_from_sybmol.cache_clear()
        print(snd_exchange.get_info_from_sybmol.cache_info())


        dict_id_sumbol = {}
        dict_sumbol_id = {}
        start_top = 0
        start_top_2 = 0
        last_i = 0
        for i, from_token in enumerate(fst_exchange.get_all_token_name()):
            dict_id_sumbol[from_token + "fstex"] = i
            dict_sumbol_id[i] = from_token + "fstex"
            if from_token == "RUB":
                start_top = i
            last_i = i

        last_i += 1
        for from_token in snd_exchange.get_all_token_name():
            dict_id_sumbol[from_token + "sndex"] = last_i
            dict_sumbol_id[last_i] = from_token + "sndex"
            if from_token == "RUB":
                start_top_2 = last_i
            last_i += 1

        tokens_on_other_exchange = list(set(fst_exchange.get_all_token_name()) & set(snd_exchange.get_all_token_name()))

        g = Graph(len(dict_id_sumbol))

        for el in tokens_on_other_exchange:
            if el not in BLACKLIST:
                g.addEdge(dict_id_sumbol[el + "sndex"], dict_id_sumbol[el + "fstex"], math.log(1))
                g.addEdge(dict_id_sumbol[el + "fstex"], dict_id_sumbol[el + "sndex"], math.log(1))

        q = Queue()
        for el in fst_exchange.get_all_token_name():
            q.put(el + "fstex")
        for el in snd_exchange.get_all_token_name():
            q.put(el + "sndex")

        thread1 = threading.Thread(target=created_graph, args=(q, fst_exchange, snd_exchange, dict_id_sumbol, g, BLACKLIST), daemon=True)
        thread2 = threading.Thread(target=created_graph, args=(q, fst_exchange, snd_exchange, dict_id_sumbol, g, BLACKLIST), daemon=True)
        thread3 = threading.Thread(target=created_graph, args=(q, fst_exchange, snd_exchange, dict_id_sumbol, g, BLACKLIST), daemon=True)
        thread4 = threading.Thread(target=created_graph, args=(q, fst_exchange, snd_exchange, dict_id_sumbol, g, BLACKLIST), daemon=True)
        thread5 = threading.Thread(target=created_graph, args=(q, fst_exchange, snd_exchange, dict_id_sumbol, g, BLACKLIST), daemon=True)
        thread6 = threading.Thread(target=created_graph, args=(q, fst_exchange, snd_exchange, dict_id_sumbol, g, BLACKLIST), daemon=True)
        thread7 = threading.Thread(target=created_graph, args=(q, fst_exchange, snd_exchange, dict_id_sumbol, g, BLACKLIST), daemon=True)
        thread8 = threading.Thread(target=created_graph, args=(q, fst_exchange, snd_exchange, dict_id_sumbol, g, BLACKLIST), daemon=True)


        thread1.start()
        thread2.start()
        thread3.start()
        thread4.start()
        thread5.start()
        thread6.start()
        thread7.start()
        thread8.start()

        q.join()


        g.BellmanFord(start_top)

        tmp = g.getPred(start_top)
        tmp_pre_last = 0
        tmp_last = 0

        path_trade = [(dict_sumbol_id[start_top], start_top)]
        print("in while")

        while (dict_sumbol_id[tmp], tmp) not in path_trade:
            print(dict_sumbol_id[tmp])
            if tmp == tmp_pre_last:
                break
            path_trade.append((dict_sumbol_id[tmp], tmp))
            tmp_pre_last = tmp_last
            tmp_last = tmp
            tmp = g.getPred(tmp)


        if dict_sumbol_id[tmp][-5:] == "fstex":
            path_trade.append((dict_sumbol_id[start_top], start_top))
        else:
            path_trade.append((dict_sumbol_id[start_top_2], start_top_2))

        print(path_trade)
		


        path_trade_price = []
        for i in range(len(path_trade) - 1):
            from_t = path_trade[i]
            to_t   = path_trade[i + 1]

            if to_t == from_t:
                del path_trade[i]
                continue
            
            if (from_t[0])[:-5] == (to_t[0])[:-5]:
                price = 1
            else:
                if (from_t[0])[-5:] == "fstex":
                    price = fst_exchange.get_absolute_token_price((from_t[0])[:-5], (to_t[0])[:-5])
                else:
                    price = snd_exchange.get_absolute_token_price((from_t[0])[:-5], (to_t[0])[:-5])
            if (from_t[0])[-5:] == "fstex":
                path_trade_price.append((from_t, to_t, fst_exchange.get_correct_symbol((from_t[0])[:-5], (to_t[0])[:-5]), price))
            else:
                path_trade_price.append((from_t, to_t, snd_exchange.get_correct_symbol((from_t[0])[:-5], (to_t[0])[:-5]), price))


        return path_trade_price



def get_path_from(from_ex, to_ex):
	global MONEY
	money = MONEY

	flag = 1
	path_trade = arbitrage_main(from_ex[0], to_ex[0], from_ex[2] + to_ex[2])


	message_text = ""
	if flag:
		for from_t, to_t, symbol, _ in path_trade:
			if (from_t[0])[:-5] == (to_t[0])[:-5]:
				continue
			else:
				if (from_t[0])[-5:] == "fstex":
					price = from_ex[0].get_absolute_token_price((from_t[0])[:-5], (to_t[0])[:-5])
				else:
					price = to_ex[0].get_absolute_token_price((from_t[0])[:-5], (to_t[0])[:-5])
			message_text += str(from_t[0]) + "/" + str(to_t[0]) + "\n" + str(price) + "\n\n"
			if (from_t[0])[:-5] == symbol[:len((from_t[0])[:-5])]:
				money = money * price
			else:
				money = money / price

			if (to_t[0])[:-5] == "RUB":
				message_text = message_text.replace("fstex", from_ex[1])
				message_text = message_text.replace("sndex", to_ex[1])
				print(message_text)
				if money > MONEY:
					print("✅" + str(money) + '\n' + str(((money-MONEY)/MONEY) * 100) + "%")
				else:
					print("❌" + str(money) + '\n' + str(((money-MONEY)/MONEY) * 100) + "%")

				message_text = ""
				money = MONEY
    

if __name__ == "__main__":
    session = spot.HTTP(
        endpoint='https://api.bybit.com', 
        api_key=api_key,
        api_secret=api_secret
    )
    bybit = exchange.Bybit(session)	
    huobi = exchange.Huobi()


    get_path_from((huobi, "huobi", []), (bybit, "bybit", []))