# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.async_support.base.exchange import Exchange

# -----------------------------------------------------------------------------

try:
    basestring  # Python 3
except NameError:
    basestring = str  # Python 2
import hashlib
from ccxt.base.errors import ExchangeError
from ccxt.base.errors import AuthenticationError
from ccxt.base.errors import BadSymbol
from ccxt.base.errors import InsufficientFunds
from ccxt.base.errors import InvalidOrder


class lakebtc(Exchange):

    def describe(self):
        return self.deep_extend(super(lakebtc, self).describe(), {
            'id': 'lakebtc',
            'name': 'LakeBTC',
            'countries': ['US'],
            'version': 'api_v2',
            'rateLimit': 1000,
            'has': {
                'cancelOrder': True,
                'CORS': True,
                'createMarketOrder': False,
                'createOrder': True,
                'fetchBalance': True,
                'fetchMarkets': True,
                'fetchOrderBook': True,
                'fetchTicker': True,
                'fetchTickers': True,
                'fetchTrades': True,
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/28074120-72b7c38a-6660-11e7-92d9-d9027502281d.jpg',
                'api': 'https://api.lakebtc.com',
                'www': 'https://www.lakebtc.com',
                'doc': [
                    'https://www.lakebtc.com/s/api_v2',
                    'https://www.lakebtc.com/s/api',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        'bcorderbook',
                        'bctrades',
                        'ticker',
                    ],
                },
                'private': {
                    'post': [
                        'buyOrder',
                        'cancelOrders',
                        'getAccountInfo',
                        'getExternalAccounts',
                        'getOrders',
                        'getTrades',
                        'openOrders',
                        'sellOrder',
                    ],
                },
            },
            'fees': {
                'trading': {
                    'maker': 0.15 / 100,
                    'taker': 0.2 / 100,
                },
            },
            'exceptions': {
                'broad': {
                    'Signature': AuthenticationError,
                    'invalid symbol': BadSymbol,
                    'Volume doit': InvalidOrder,
                    'insufficient_balance': InsufficientFunds,
                },
            },
        })

    async def fetch_markets(self, params={}):
        response = await self.publicGetTicker(params)
        result = []
        keys = list(response.keys())
        for i in range(0, len(keys)):
            id = keys[i]
            market = response[id]
            baseId = id[0:3]
            quoteId = id[3:6]
            base = baseId.upper()
            quote = quoteId.upper()
            symbol = base + '/' + quote
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'baseId': baseId,
                'quoteId': quoteId,
                'info': market,
                'active': None,
                'precision': self.precision,
                'limits': self.limits,
            })
        return result

    async def fetch_balance(self, params={}):
        await self.load_markets()
        response = await self.privatePostGetAccountInfo(params)
        balances = self.safe_value(response, 'balance', {})
        result = {'info': response}
        currencyIds = list(balances.keys())
        for i in range(0, len(currencyIds)):
            currencyId = currencyIds[i]
            code = self.safe_currency_code(currencyId)
            account = self.account()
            account['total'] = self.safe_float(balances, currencyId)
            result[code] = account
        return self.parse_balance(result)

    async def fetch_order_book(self, symbol, limit=None, params={}):
        await self.load_markets()
        request = {
            'symbol': self.market_id(symbol),
        }
        response = await self.publicGetBcorderbook(self.extend(request, params))
        return self.parse_order_book(response)

    def parse_ticker(self, ticker, market=None):
        timestamp = self.milliseconds()
        symbol = None
        if market is not None:
            symbol = market['symbol']
        last = self.safe_float(ticker, 'last')
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': self.safe_float(ticker, 'high'),
            'low': self.safe_float(ticker, 'low'),
            'bid': self.safe_float(ticker, 'bid'),
            'bidVolume': None,
            'ask': self.safe_float(ticker, 'ask'),
            'askVolume': None,
            'vwap': None,
            'open': None,
            'close': last,
            'last': last,
            'previousClose': None,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': self.safe_float(ticker, 'volume'),
            'quoteVolume': None,
            'info': ticker,
        }

    async def fetch_tickers(self, symbols=None, params={}):
        await self.load_markets()
        response = await self.publicGetTicker(params)
        ids = list(response.keys())
        result = {}
        for i in range(0, len(ids)):
            symbol = ids[i]
            ticker = response[symbol]
            market = None
            if symbol in self.markets_by_id:
                market = self.markets_by_id[symbol]
                symbol = market['symbol']
            result[symbol] = self.parse_ticker(ticker, market)
        return self.filter_by_array(result, 'symbol', symbols)

    async def fetch_ticker(self, symbol, params={}):
        await self.load_markets()
        market = self.market(symbol)
        tickers = await self.publicGetTicker(params)
        return self.parse_ticker(tickers[market['id']], market)

    def parse_trade(self, trade, market=None):
        timestamp = self.safe_timestamp(trade, 'date')
        id = self.safe_string(trade, 'tid')
        price = self.safe_float(trade, 'price')
        amount = self.safe_float(trade, 'amount')
        cost = None
        if price is not None:
            if amount is not None:
                cost = price * amount
        symbol = None
        if market is not None:
            symbol = market['symbol']
        return {
            'id': id,
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'order': None,
            'type': None,
            'side': None,
            'takerOrMaker': None,
            'price': price,
            'amount': amount,
            'cost': cost,
            'fee': None,
        }

    async def fetch_trades(self, symbol, since=None, limit=None, params={}):
        await self.load_markets()
        market = self.market(symbol)
        request = {
            'symbol': market['id'],
        }
        response = await self.publicGetBctrades(self.extend(request, params))
        return self.parse_trades(response, market, since, limit)

    async def create_order(self, symbol, type, side, amount, price=None, params={}):
        await self.load_markets()
        if type == 'market':
            raise ExchangeError(self.id + ' allows limit orders only')
        method = 'privatePost' + self.capitalize(side) + 'Order'
        market = self.market(symbol)
        order = {
            'params': [price, amount, market['id']],
        }
        response = await getattr(self, method)(self.extend(order, params))
        return {
            'info': response,
            'id': self.safe_string(response, 'id'),
        }

    async def cancel_order(self, id, symbol=None, params={}):
        await self.load_markets()
        request = {
            'params': [id],
        }
        return await self.privatePostCancelOrder(self.extend(request, params))

    def nonce(self):
        return self.microseconds()

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.version
        if api == 'public':
            url += '/' + path
            if params:
                url += '?' + self.urlencode(params)
        else:
            self.check_required_credentials()
            nonce = self.nonce()
            nonceAsString = str(nonce)
            requestId = self.seconds()
            queryParams = ''
            if 'params' in params:
                paramsList = params['params']
                stringParams = []
                for i in range(0, len(paramsList)):
                    param = paramsList[i]
                    if not isinstance(paramsList, basestring):
                        param = str(param)
                    stringParams.append(param)
                queryParams = ','.join(stringParams)
                body = {
                    'method': path,
                    'params': params['params'],
                    'id': requestId,
                }
            else:
                body = {
                    'method': path,
                    'params': '',
                    'id': requestId,
                }
            body = self.json(body)
            query = [
                'tonce=' + nonceAsString,
                'accesskey=' + self.apiKey,
                'requestmethod=' + method.lower(),
                'id=' + str(requestId),
                'method=' + path,
                'params=' + queryParams,
            ]
            query = '&'.join(query)
            signature = self.hmac(self.encode(query), self.encode(self.secret), hashlib.sha1)
            auth = self.encode(self.apiKey + ':' + signature)
            signature64 = self.decode(self.string_to_base64(auth))
            headers = {
                'Json-Rpc-Tonce': nonceAsString,
                'Authorization': 'Basic ' + signature64,
                'Content-Type': 'application/json',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def handle_errors(self, code, reason, url, method, headers, body, response, requestHeaders, requestBody):
        if response is None:
            return  # fallback to the default error handler
        #
        #     {"error":"Failed to submit order: invalid symbol"}
        #     {"error":"Failed to submit order: La validation a échoué : Volume doit être supérieur ou égal à 1.0"}
        #     {"error":"Failed to submit order: insufficient_balance"}
        #
        feedback = self.id + ' ' + body
        error = self.safe_string(response, 'error')
        if error is not None:
            self.throw_broadly_matched_exception(self.exceptions['broad'], error, feedback)
            raise ExchangeError(feedback)  # unknown message
