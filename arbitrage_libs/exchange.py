from pybit import spot
import requests
import json
from .token import Token
import time

from functools import lru_cache

from .config import MONEY, INDEX_P2P_ORDER
from .config import SYMBOLS_FOR_TRADE

class Exchange():
    def __init__(self, _session):
        self.session = _session
    
    #@dev ошибка возникает в моменте когда торговая пара выглядит как ltc/btc в этом случае не правильно считается колво usdt
    def get_prices_from_orederbook(self, for_buy, for_sell):
        price_for_buy = 0
        price_for_sell = 0

        money_work = 0
        money_start = 0
        for el in for_buy:
            if money_work > MONEY:
                break
                
            # конкретно здесь
            money_work += float(el[0]) * float(el[1])
            money_start += float(el[1])
        # if money_work < 1000:
        #     return (1, 1)

        price_for_buy = (money_work/money_start)

        money_work = 0
        money_start = 0
        for el in for_sell:
            if money_work > MONEY:
                break

            money_work += float(el[0]) * float(el[1])
            money_start += float(el[1])

        price_for_sell = (money_work/money_start)
        # дебаг тема тк нужно выодить price_for_sell price_for_buy
        #return (for_buy[0][0], for_sell[1][0])
        return(price_for_buy, price_for_sell)

    def check_token_pair(self, from_token, to_token):
        if ((from_token, to_token) in self.symbols_all_pairs) or ((to_token, from_token) in self.symbols_all_pairs):
            return 1
        else:
            return 0

    # @dev must return dict {"ton" : ["eth", "usdt"]} it means we will buy eth for ton, for example we will give 1 ton, and get 10eth
    def get_all_tokens(self) -> dict:
        pass
    
    def get_pair_tokens(self) -> list:
        pass

    def get_absolute_token_price(self, from_token, to_token) -> float:
        pass

    def get_price_token_pair(self, from_token, to_token) -> float:
        pass

class Huobi(Exchange):
    def __init__(self):
        symbols_all_pairs_p2p = [
            ("USDT","RUB"),
            ("BTC", "RUB"),
            ("USDD", "RUB"),
            ("HTX", "RUB"),
            ("TRX", "RUB"),
            ("ETH", "RUB"),
            ("EOS", "RUB"),
            ("XRP", "RUB"),
            ("LTC", "RUB"),
        ]
        self.coinIds_p2p = {
            "USDT" : 2,
            "BTC"  : 1,
            "USDD" : 62,
            "HTX"  : 65,
            "TRX"  : 22,
            "ETH"  : 3, 
            "EOS"  : 5,
            "XRP"  : 7,
            "LTC"  : 8
        }
        self.dict_of_pay_method = {
            "Sber" : 29,
            "Tinkoff" : 28,
            "Sbp" : 69,
            "Raiffazen" : 36
        }
        
        symbols_all_pairs = set()
        for i in range(0, 301, 50):
            json_symbols_all_pairs = requests.get(url="https://coinranking.com/api/v2/exchange/xRvYoPjeQ/markets?offset={}&orderDirection=desc&referenceCurrencyUuid=yhjMzLPhuIDl&limit=50".format(str(i))).json()
            json_symbols_all_pairs = json_symbols_all_pairs["data"]["markets"]
            for el in json_symbols_all_pairs:
                if (el["base"]["symbol"] in SYMBOLS_FOR_TRADE) and (el["quote"]["symbol"] in SYMBOLS_FOR_TRADE):
                    symbols_all_pairs.add((el["base"]["symbol"], el["quote"]["symbol"]))
        
        self.symbols_all_pairs = list(symbols_all_pairs) + list(symbols_all_pairs_p2p)

        all_token_name = set()
        for el in self.symbols_all_pairs:
            all_token_name.add(el[0])
            all_token_name.add(el[1])
        

        self.all_token_name = list(all_token_name)

        all_tokens = {}
        for el in self.all_token_name:
            tmp_token_pair_for_buy = []
            for symbol in self.symbols_all_pairs:
                if symbol[1] == el:
                    tmp_token_pair_for_buy.append(symbol[0])
                if symbol[0] == el:
                    tmp_token_pair_for_buy.append(symbol[1])

            if len(tmp_token_pair_for_buy) != 0:
                all_tokens[el] = Token(el, "Huobi", tmp_token_pair_for_buy)

        self.all_tokens = all_tokens

    def get_all_tokens(self):
        return self.all_tokens

    def get_all_token_name(self):
        return self.all_token_name

    @lru_cache(maxsize=None)
    def get_info_from_sybmol(self, symbol):
        #info_from_pair = self.session.latest_information_for_symbol(symbol=symbol)
        if "RUB" in symbol:
            token_of_symbol = self.coinIds_p2p[symbol[3:]] if symbol.find('RUB') == 0 else self.coinIds_p2p[symbol[:-3]]
            trades_buy = json.loads(requests.get("https://www.htx.com" + f"/-/x/otc/v1/data/trade-market?coinId={token_of_symbol}&currency=11&tradeType=sell&currPage=1&payMethod={self.dict_of_pay_method['Sber']},{self.dict_of_pay_method['Sbp']},{self.dict_of_pay_method['Raiffazen']}&acceptOrder=0&country=&blockType=general&online=1&range=0&amount=&isThumbsUp=false&isMerchant=false&isTraded=false&onlyTradable=false&isFollowed=false").text)
            trades_sell = json.loads(requests.get("https://www.htx.com" + f"/-/x/otc/v1/data/trade-market?coinId={token_of_symbol}&currency=11&tradeType=buy&currPage=1&payMethod={self.dict_of_pay_method['Sber']},{self.dict_of_pay_method['Sbp']},{self.dict_of_pay_method['Raiffazen']}&acceptOrder=-1&country=&blockType=general&online=1&range=0&amount=&isThumbsUp=false&isMerchant=false&isTraded=false&onlyTradable=false&isFollowed=false").text)

            return {"result" : {"askPrice" : trades_buy["data"][INDEX_P2P_ORDER]["price"], "bidPrice" : trades_sell["data"][INDEX_P2P_ORDER]["price"]}}

        for_buy = json.loads(requests.get(f"https://api.huobi.pro/market/depth?symbol={str(symbol).lower()}&type=step0&depth=10").text)["tick"]["asks"]
        for_sell = json.loads(requests.get(f"https://api.huobi.pro/market/depth?symbol={str(symbol).lower()}&type=step0&depth=10").text)["tick"]["bids"]

        prices = self.get_prices_from_orederbook(for_buy, for_sell)

        price_for_buy = prices[0]
        price_for_sell = prices[1]

        #info_from_pair = self.session.last_traded_price(symbol=symbol)
        return {"result" : {"askPrice" : price_for_buy, "bidPrice" : price_for_sell}}
    
    def get_correct_symbol(self, from_token, to_token):
        symbol = (from_token + to_token) if (from_token, to_token) in self.symbols_all_pairs else (to_token + from_token)
        return symbol

    def get_absolute_token_price(self, from_token, to_token):
        flag_buy = True
        symbol = self.get_correct_symbol(from_token, to_token)
        if from_token == symbol[:len(from_token)]: # проблема здесь я думаю должно быть не usdt, тк не всегда мы продаем на usdt
            flag_buy = False
        
        if "RUB" in symbol:
            token_of_symbol = self.coinIds_p2p[symbol[3:]] if symbol.find('RUB') == 0 else self.coinIds_p2p[symbol[:-3]]
            trades_buy = json.loads(requests.get("https://www.htx.com" + f"/-/x/otc/v1/data/trade-market?coinId={token_of_symbol}&currency=11&tradeType=sell&currPage=1&payMethod={self.dict_of_pay_method['Sber']},{self.dict_of_pay_method['Sbp']},{self.dict_of_pay_method['Raiffazen']}&acceptOrder=0&country=&blockType=general&online=1&range=0&amount=&isThumbsUp=false&isMerchant=false&isTraded=false&onlyTradable=false&isFollowed=false").text)
            trades_sell = json.loads(requests.get("https://www.htx.com" + f"/-/x/otc/v1/data/trade-market?coinId={token_of_symbol}&currency=11&tradeType=buy&currPage=1&payMethod={self.dict_of_pay_method['Sber']},{self.dict_of_pay_method['Sbp']},{self.dict_of_pay_method['Raiffazen']}&acceptOrder=-1&country=&blockType=general&online=1&range=0&amount=&isThumbsUp=false&isMerchant=false&isTraded=false&onlyTradable=false&isFollowed=false").text)

            if flag_buy:
                # from 1 token we take n tokens
                return float(trades_buy["data"][INDEX_P2P_ORDER]["price"])
            else:
                # from n token we take 1 tokens
                return float(trades_sell["data"][INDEX_P2P_ORDER]["price"]) #/1
        
        for_buy = json.loads(requests.get(f"https://api.huobi.pro/market/depth?symbol={str(symbol).lower()}&type=step0&depth=10").text)["tick"]["asks"]
        for_sell = json.loads(requests.get(f"https://api.huobi.pro/market/depth?symbol={str(symbol).lower()}&type=step0&depth=10").text)["tick"]["bids"]


        prices = self.get_prices_from_orederbook(for_buy, for_sell)

        price_for_buy = prices[0]
        price_for_sell = prices[1]

        info_from_pair = {"result" : {"askPrice" : price_for_buy, "bidPrice" : price_for_sell}}

        
        if flag_buy:
            # from 1 token we take n tokens
            return float(info_from_pair["result"]["askPrice"])
        else:
            # from n token we take 1 tokens
            return float(info_from_pair["result"]["bidPrice"]) #/1
    
    def get_price_token_pair(self, from_token, to_token):
        # новая версия попоробовал иправить косяк с ценообразованием вроде вышло) но цены еще берутся неправильно не покупка и продажу а просто ласт цена
        flag_buy = True
        symbol = self.get_correct_symbol(from_token, to_token)
        if from_token == symbol[:len(from_token)]: # проблема здесь я думаю должно быть не usdt, тк не всегда мы продаем на usdt
            flag_buy = False

        info_from_pair = self.get_info_from_sybmol(symbol)

        # изменил ценообразование всязи с полным описанием в example
        if flag_buy:
            # from 1 token we take n tokens
            return 1/float(info_from_pair["result"]["bidPrice"])
            #return 1/float(info_from_pair["result"]["price"])
        else:
            # from n token we take 1 tokens
            return float(info_from_pair["result"]["askPrice"]) #/1
            #return float(info_from_pair["result"]["price"])
        

class Bybit(Exchange):
    def __init__(self, _session):
        super().__init__(_session)
        self.ENDURL_P2P = "https://api2.bybit.com"
        symbols_all_pairs_p2p = [
            ("USDT", "RUB"), 
            ("BTC", "RUB"),
            ("ETH", "RUB"),
            ("USDC", "RUB")
        ]
        list_of_pairs_p2p = ["RUB", "USDT", "BTC", "ETH", "USDC"]

        # Для p2p нет смысла перебирать все токены достаточно только те которые торгуются на p2p

        blacklist = ["PEPE2.0", "stETH", 'TWT']
        symbols_all_pairs = []
        for i in range(0, 301, 50):
            json_symbols_all_pairs = requests.get(url="https://coinranking.com/api/v2/exchange/TjMe3QlK0/markets?offset={}&orderDirection=desc&referenceCurrencyUuid=yhjMzLPhuIDl&limit=50".format(str(i))).json()
            json_symbols_all_pairs = json_symbols_all_pairs["data"]["markets"]
            
            for el in json_symbols_all_pairs:
                if el["base"]["symbol"] not in blacklist and el["quote"]["symbol"] not in blacklist:
                    if ((el["base"]["symbol"] in SYMBOLS_FOR_TRADE) and (el["quote"]["symbol"] in SYMBOLS_FOR_TRADE)):
                        symbols_all_pairs.append((el["base"]["symbol"], el["quote"]["symbol"]))
        
        self.symbols_all_pairs = symbols_all_pairs + symbols_all_pairs_p2p

        all_token_name = set()
        for el in self.symbols_all_pairs:
            all_token_name.add(el[0])
            all_token_name.add(el[1])
        
        self.all_token_name = all_token_name

        all_tokens = {}
        for el in self.all_token_name:
            tmp_token_pair_for_buy = []
            for symbol in self.symbols_all_pairs:
                if symbol[1] == el:
                    tmp_token_pair_for_buy.append(symbol[0])
                if symbol[0] == el:
                    tmp_token_pair_for_buy.append(symbol[1])

            if len(tmp_token_pair_for_buy) != 0:
                all_tokens[el] = Token(el, "Bybit", tmp_token_pair_for_buy)

        self.all_tokens = all_tokens
        
    def get_all_tokens(self):
        return self.all_tokens

    def get_all_token_name(self):
        return self.all_token_name
    
    @lru_cache(maxsize=None)
    def get_info_from_sybmol(self, symbol):
        if "RUB" in symbol:
            token_of_symbol = symbol[3:] if symbol.find('RUB') == 0 else symbol[:-3]

            payload_buy  = {"userId":"","tokenId": token_of_symbol,"currencyId":"RUB","payment":["582"],"side":"1","size":"5","page":"1","amount":"","authMaker":"false","canTrade":"false"}
            payload_sell = {"userId":"","tokenId": token_of_symbol,"currencyId":"RUB","payment":["582"],"side":"0","size":"5","page":"1","amount":"","authMaker":"false","canTrade":"false"}

            trades_buy  = json.loads(requests.post(url=(self.ENDURL_P2P  + "/fiat/otc/item/online"), data=payload_buy).text)
            trades_sell = json.loads(requests.post(url=(self.ENDURL_P2P  + "/fiat/otc/item/online"), data=payload_sell).text)


            return {"result" : {"askPrice" : trades_buy["result"]["items"][INDEX_P2P_ORDER]["price"], "bidPrice" : trades_sell["result"]["items"][INDEX_P2P_ORDER]["price"]}}

        #info_from_pair = self.session.latest_information_for_symbol(symbol=symbol)
        for_buy = self.session.orderbook(symbol=symbol)["result"]["asks"]
        for_sell = self.session.orderbook(symbol=symbol)["result"]["bids"]

        prices = self.get_prices_from_orederbook(for_buy, for_sell)

        price_for_buy = prices[0]
        price_for_sell = prices[1]

        #info_from_pair = self.session.last_traded_price(symbol=symbol)
        return {"result" : {"askPrice" : price_for_buy, "bidPrice" : price_for_sell}}

    def get_correct_symbol(self, from_token, to_token):
        symbol = (from_token + to_token) if (from_token, to_token) in self.symbols_all_pairs else (to_token + from_token)
        return symbol

    def get_absolute_token_price(self, from_token, to_token):
        flag_buy = True
        symbol = self.get_correct_symbol(from_token, to_token)
        if from_token == symbol[:len(from_token)]: # проблема здесь я думаю должно быть не usdt, тк не всегда мы продаем на usdt
            flag_buy = False

        if "RUB" in symbol:
            token_of_symbol = symbol[3:] if symbol.find('RUB') == 0 else symbol[:-3]


            payload_buy  = {"userId":"","tokenId": token_of_symbol,"currencyId":"RUB","payment":["582"],"side":"1","size":"5","page":"1","amount":"","authMaker":"false","canTrade":"false"}
            payload_sell = {"userId":"","tokenId": token_of_symbol,"currencyId":"RUB","payment":["582"],"side":"0","size":"5","page":"1","amount":"","authMaker":"false","canTrade":"false"}

            trades_buy  = json.loads(requests.post(url=(self.ENDURL_P2P  + "/fiat/otc/item/online"), data=payload_buy).text)
            trades_sell = json.loads(requests.post(url=(self.ENDURL_P2P  + "/fiat/otc/item/online"), data=payload_sell).text)

            if flag_buy:
                # from 1 token we take n tokens
                return float(trades_buy["result"]["items"][INDEX_P2P_ORDER]["price"])
            else:
                # from n token we take 1 tokens
                return float(trades_sell["result"]["items"][INDEX_P2P_ORDER]["price"]) #/1

        for_buy = self.session.orderbook(symbol=symbol)["result"]["asks"]
        for_sell = self.session.orderbook(symbol=symbol)["result"]["bids"]


        prices = self.get_prices_from_orederbook(for_buy, for_sell)

        price_for_buy = prices[0]
        price_for_sell = prices[1]

        info_from_pair = {"result" : {"askPrice" : price_for_buy, "bidPrice" : price_for_sell}}

        
        if flag_buy:
            # from 1 token we take n tokens
            return float(info_from_pair["result"]["askPrice"])
        else:
            # from n token we take 1 tokens
            return float(info_from_pair["result"]["bidPrice"]) #/1


    def get_price_token_pair(self, from_token, to_token):
        # новая версия попоробовал иправить косяк с ценообразованием вроде вышло) но цены еще берутся неправильно не покупка и продажу а просто ласт цена
        flag_buy = True
        symbol = self.get_correct_symbol(from_token, to_token)
        if from_token == symbol[:len(from_token)]: # проблема здесь я думаю должно быть не usdt, тк не всегда мы продаем на usdt
            flag_buy = False

        info_from_pair = self.get_info_from_sybmol(symbol)

        # изменил ценообразование всязи с полным описанием в example
        if flag_buy:
            # from 1 token we take n tokens
            return 1/float(info_from_pair["result"]["bidPrice"])
            #return 1/float(info_from_pair["result"]["price"])
        else:
            # from n token we take 1 tokens
            return float(info_from_pair["result"]["askPrice"]) #/1
            #return float(info_from_pair["result"]["price"])