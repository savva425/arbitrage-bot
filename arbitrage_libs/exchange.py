from pybit import spot
import requests
from .token import Token

from functools import lru_cache

class Exchange():
    def __init__(self, _session):
        self.session = _session
    
    # @dev must return dict {"ton" : ["eth", "usdt"]} it means we will buy eth for ton, for example we will give 1 ton, and get 10eth
    def get_all_tokens(self) -> dict:
        pass
    
    def get_pair_tokens(self) -> list:
        pass

    def get_absolute_token_price(self, from_token, to_token) -> float:
        pass

    def get_price_token_pair(self, from_token, to_token) -> float:
        pass

class Bybit(Exchange):
    def __init__(self, _session):
        super().__init__(_session)
        symbols_all_pairs = []
        for i in range(0, 301, 50):
            json_symbols_all_pairs = requests.get(url="https://coinranking.com/api/v2/exchange/TjMe3QlK0/markets?offset={}&orderDirection=desc&referenceCurrencyUuid=yhjMzLPhuIDl&limit=50".format(str(i))).json()
            json_symbols_all_pairs = json_symbols_all_pairs["data"]["markets"]

            for el in json_symbols_all_pairs:
                symbols_all_pairs.append((el["base"]["symbol"], el["quote"]["symbol"]))
        self.symbols_all_pairs = symbols_all_pairs

        all_token_name = set()
        for el in symbols_all_pairs:
            all_token_name.add(el[0])
            all_token_name.add(el[1])
        
        self.all_token_name = all_token_name

        all_tokens = {}
        for el in all_token_name:
            tmp_token_pair_for_buy = []
            for symbol in symbols_all_pairs:
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
        #info_from_pair = self.session.latest_information_for_symbol(symbol=symbol)
        info_from_pair = self.session.best_bid_ask_price(symbol=symbol)
        #info_from_pair = self.session.last_traded_price(symbol=symbol)
        return info_from_pair

    def get_correct_symbol(self, from_token, to_token):
        symbol = (from_token + to_token) if (from_token, to_token) in self.symbols_all_pairs else (to_token + from_token)
        return symbol

    def get_absolute_token_price(self, from_token, to_token):
        flag_buy = True
        symbol = self.get_correct_symbol(from_token, to_token)
        if from_token == symbol[:len(from_token)]: # проблема здесь я думаю должно быть не usdt, тк не всегда мы продаем на usdt
            flag_buy = False

        info_from_pair = self.session.best_bid_ask_price(symbol=symbol)

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
