#@dev add base monet usd, not usdt and trade about usd because usd on all excange have stable course
class Token():
    # _name - name of token, for example usdt
    # _exch_name - exchange name, for example binance
    # *args - all token pairs, for example [ton, eth] its denotes for example usdt/ton, usdt/eth
    # **kwargs - all price for tokens pair, for example {ton: 2.24/1} for usdt/ton
    ### where ton = Token("ton", "bybit", tokens_pair)

    def __init__(self, _name, _exch_name, _tokens_pair):
        self.name = _name
        self.exch_name = _exch_name
        self.tokens_pair = _tokens_pair
    
    def get_all_token_pairs(self):
        return self.tokens_pair