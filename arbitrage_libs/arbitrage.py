from collections import defaultdict 

import threading
from queue import Queue

from arbitrage_libs import exchange
from arbitrage_libs.graph import Graph

import math


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
			if from_token == "USDT":
				start_top = i
			last_i = i

		last_i += 1
		for from_token in snd_exchange.get_all_token_name():
			dict_id_sumbol[from_token + "sndex"] = last_i
			dict_sumbol_id[last_i] = from_token + "sndex"
			if from_token == "USDT":
				start_top_2 = last_i
			last_i += 1

		tokens_on_other_exchange = list(set(fst_exchange.get_all_token_name()) & set(snd_exchange.get_all_token_name()))

		g = Graph(len(dict_id_sumbol))

		for el in tokens_on_other_exchange:
			if el not in BLACKLIST:
				g.addEdge(dict_id_sumbol[el + "sndex"], dict_id_sumbol[el + "fstex"], math.log(1))
				g.addEdge(dict_id_sumbol[el + "fstex"], dict_id_sumbol[el + "sndex"], math.log(1))


		def created_graph(q):
			while q.empty() == False:
				from_token = q.get()
				#print(from_token, end=" - ")
				if from_token[:-5] not in BLACKLIST:
					if from_token[-5:] == "fstex":
						for to_token in fst_exchange.get_all_tokens()[from_token[:-5]].get_all_token_pairs():
							# предположил что нужно поменять to и from тк мы вычесляем немного иначе
							# короче мы же вычесляем самую выгодную сделку, а она по алгоритму получается самой наооборот невыгодной то есть по курсу который
							# в конце мы должны купить а не продать, перечитать еше раз алгоритм арбитража
							#print(dict_id_sumbol[from_token], dict_id_sumbol[to_token], bybit.get_price_token_pair(from_token, to_token), end=" ")
							if fst_exchange.check_token_pair(from_token[:-5], to_token):
								try:
									g.addEdge(dict_id_sumbol[from_token], dict_id_sumbol[to_token + "fstex"], math.log(fst_exchange.get_price_token_pair(from_token[:-5], to_token)))
								except:
									pass
					else:
						for to_token in snd_exchange.get_all_tokens()[from_token[:-5]].get_all_token_pairs():
							# предположил что нужно поменять to и from тк мы вычесляем немного иначе
							# короче мы же вычесляем самую выгодную сделку, а она по алгоритму получается самой наооборот невыгодной то есть по курсу который
							# в конце мы должны купить а не продать, перечитать еше раз алгоритм арбитража
							#print(dict_id_sumbol[from_token], dict_id_sumbol[to_token], bybit.get_price_token_pair(from_token, to_token), end=" ")
							if snd_exchange.check_token_pair(from_token[:-5], to_token):
								try:
									g.addEdge(dict_id_sumbol[from_token], dict_id_sumbol[to_token + "sndex"], math.log(snd_exchange.get_price_token_pair(from_token[:-5], to_token)))
								except:
									pass
				q.task_done()


		q = Queue()
		for el in fst_exchange.get_all_token_name():
			q.put(el + "fstex")
		for el in snd_exchange.get_all_token_name():
			q.put(el + "sndex")

		thread1 = threading.Thread(target=created_graph, args=(q,), daemon=True)
		thread2 = threading.Thread(target=created_graph, args=(q,), daemon=True)
		thread3 = threading.Thread(target=created_graph, args=(q,), daemon=True)
		thread4 = threading.Thread(target=created_graph, args=(q,), daemon=True)
		thread5 = threading.Thread(target=created_graph, args=(q,), daemon=True)
		thread6 = threading.Thread(target=created_graph, args=(q,), daemon=True)
		thread7 = threading.Thread(target=created_graph, args=(q,), daemon=True)
		thread8 = threading.Thread(target=created_graph, args=(q,), daemon=True)


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
		#print(dict_sumbol_id_bybit[start_top], start_top)
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
		
		print(path_trade)

		if dict_sumbol_id[tmp][-5:] == "fstex":
			path_trade.append((dict_sumbol_id[start_top], start_top))
		else:
			path_trade.append((dict_sumbol_id[start_top_2], start_top_2))
		


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
			#print(from_t, to_t, bybit.get_correct_symbol(from_t[0], to_t[0]), price)



		return path_trade_price

		# if money > 1005:
		# 	for from_t, to_t, symbol, price in path_trade_price:
		# 		if from_t[0] == symbol[:len(from_t[0])]:
		# 			order = place_order("SELL", symbol, from_t[0])
		# 		else:
		# 			order = place_order("BUY", symbol, from_t[0])
		# 		print(order)


		# изменить чтобы получал цену покупки для одного и цену продажи именно для биржи для подсчета самих путей 
		# хотя вроде ничего не изменилось и выводит странные сделки разобраться с этим

		# можно изменить и оставить то что есть и искать сделки с стандартным обменным курсом типо last_trade а потом просто среди них искать прибыльную


		# path_trade_price = path_trade_price[::-1]
		# money = 800
		# for to_t, from_t, symbol, _ in path_trade_price:
		# 	if (from_t[0])[:-5] == (to_t[0])[:-5]:
		# 		continue
		# 	else:
		# 		if (from_t[0])[-5:] == "bybit":
		# 			price = bybit.get_absolute_token_price((from_t[0])[:-5], (to_t[0])[:-5])
		# 		else:
		# 			price = bitget.get_absolute_token_price((from_t[0])[:-5], (to_t[0])[:-5])
		# 	print(from_t, to_t, price)
		# 	if (from_t[0])[:-5] == symbol[:len((from_t[0])[:-5])]:
		# 		money = money * price
		# 	else:
		# 		money = money / price
		# print(money)
		# if money > 800:
		# 	with open("logfile.txt", "a") as f:
		# 		f.write(str(money) + "\n")