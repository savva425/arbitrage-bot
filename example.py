from collections import defaultdict 

import threading
from queue import Queue

import time

import math
from pybit import spot
import requests
from arbitrage_libs import exchange

# Class to represent a graph 
class Graph: 
	def __init__(self, vertices): 
		self.V = vertices # No. of vertices 
		self.graph = [] # default dictionary to store graph 

	# function to add an edge to graph 
	def addEdge(self, u, v, w): 
		self.graph.append([u, v, w]) 

	# utility function used to print the solution 
	def getDist(self, dist): 
		print("Vertex Distance from Source") 
		for i in range(self.V): 
			print("% d \t\t % d" % (i, dist[i])) 
	def getPred(self, to):
		return self.pred[to]

	# The main function that finds shortest distances from src to 
	# all other vertices using Bellman-Ford algorithm. The function 
	# also detects negative weight cycle 
	def BellmanFord(self, src): 
		# Step 1: Initialize distances from src to all other vertices 
		# as INFINITE 
		pred = [src] * self.V
		dist = [float("Inf")] * self.V
		dist[src] = 0


		# Step 2: Relax all edges |V| - 1 times. A simple shortest 
		# path from src to any other vertex can have at-most |V| - 1 
		# edges 
		# тут убрал для проверки
			# Update dist value and parent index of the adjacent vertices of 
			# the picked vertex. Consider only those vertices which are still in 
			# queue
		for i in range(self.V - 1): 
			for u, v, w in self.graph: 
				if dist[u] != float("Inf") and dist[u] + w < dist[v]: 
						dist[v] = dist[u] + w
		# Step 3: check for negative-weight cycles. The above step 
		# guarantees shortest distances if graph doesn't contain 
		# negative weight cycle. If we get a shorter path, then there 
		# is a cycle.

		#self.getDist(dist)

		for u, v, w in self.graph: 
			if dist[u] != float("Inf") and dist[u] + w < dist[v]: 
				dist[v] = dist[u] + w
				pred[v] = u
		self.pred = pred

while True:
	session = spot.HTTP(
		endpoint='https://api.bybit.com', 
		api_key='9moZh8QjNSEPtqqmNk',
		api_secret='eiPv6Vu4OgDxINoFRu04d8QW6hwf7fUXgjJm'
	)
	bybit = exchange.Bybit(session)
	print(bybit.get_info_from_sybmol.cache_info())
	bybit.get_info_from_sybmol.cache_clear()
	print(bybit.get_info_from_sybmol.cache_info())

	dict_id_sumbol = {}
	dict_sumbol_id = {}
	start_top = 0
	for i, from_token in enumerate(bybit.get_all_token_name()):
		dict_id_sumbol[from_token] = i
		dict_sumbol_id[i] = from_token
		if from_token == "USDT":
			start_top = i

	g = Graph(len(bybit.get_all_token_name()))

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
		return last_order


	money = 900
	for from_t, to_t, symbol, _ in path_trade_price:
		price = bybit.get_absolute_token_price(from_t[0], to_t[0])
		print(from_t, to_t, price)
		if from_t[0] == symbol[:len(from_t[0])]:
			money = money * price
		else:
			money = money / price
	print(money)
	if money > 901:
		with open("logfile.txt", "a") as f:
			f.write(str(money) + "\n")

	if money > 901:
		for from_t, to_t, symbol, price in path_trade_price:
			info_from_symbol = bybit.session.best_bid_ask_price(symbol=symbol)
			price_trade = float(info_from_symbol["result"]["askPrice"])
			if from_t[0] == symbol[:len(from_t[0])]:
				order = place_order("SELL", symbol, from_t, price_trade)
			else:
				order = place_order("BUY", symbol, from_t, price_trade)
			print(order)
	# можно выставлять ордер на лучшую цену из orderbook тогда сделки будут обрабатываться максимально быстро. Либо ставить ордер на -1% от цены
	# хотя возможно это не сработает, почиать как работает маркет по какой цене он продает и покупает, возможно так будет правильнее

	# изменить чтобы получал цену покупки для одного и цену продажи именно для биржи для подсчета самих путей 
	# хотя вроде ничего не изменилось и выводит странные сделки разобраться с этим

	# можно изменить и оставить то что есть и искать сделки с стандартным обменным курсом типо last_trade а потом просто среди них искать прибыльную


	# path_trade_price = path_trade_price[::-1]
	# money = 1000
	# for to_t, from_t, symbol, _ in path_trade_price:
	# 	price = bybit.get_absolute_token_price(from_t[0], to_t[0])
	# 	print(from_t, to_t, price)
	# 	if from_t[0] == symbol[:len(from_t[0])]:
	# 		money = money * price
	# 	else:
	# 		money = money / price
	# print(money)

	# if money > 1002:
	# 	for to_t, from_t, symbol, _ in path_trade_price:
	# 		price = bybit.get_absolute_token_price(from_t[0], to_t[0])
	# 		if from_t[0] == symbol[:len(from_t[0])]:
	# 			active_order_info = place_order("BUY", symbol, from_t[0], price)
	# 		else:
	# 			active_order_info = place_order("SELL", symbol, from_t[0], price)
	# 	with open("logfile.txt", "a") as f:
	# 		f.write(str(money) + "\n")

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
