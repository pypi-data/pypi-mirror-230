from bingx.api import BingxAPI
import vcr
from bingx.secret import *
bingx = BingxAPI(API_KEY, SECRET_KEY)


@vcr.use_cassette('tests/vcr_cassettes/get_server_time.yml')
def test_get_server_time():
    """
    Request:
        GET / POST api/v1/common/server/time
    Parameters:
        null
    Response:
        {
            "code": 0,
            "msg": "",
            "currentTime": 1534431933321
        }
    code	    Int64	error code, 0 means successfully response, others means response failure
    msg	        String	Error Details Description
    currentTime	Int64	The current time of the system，unit: ms
    """
    assert bingx.get_server_time() is not None


def test_get_all_contracts():
    """
    Request:
        GET api/v1/market/getAllContracts
    Parameters:
        null
    Response:
        {
            "code": 0,
            "msg": "",
            "data": [{
                "contractId": "100",
                "symbol": "BTC-USDT",
                "name": "BTC-USDT",
                "size": "0.0001",
                "volumePrecision": 0,
                "pricePrecision": 2,
                "feeRate": 0.001,
                "tradeMinLimit": 1,
                "currency": "USDT",
                "asset": "BTC"
                }],
            ...
	    }
	code	        For error messages, 0 means normal
    msg	            Error message description
    contractId	    ContractId
    symbol	        Trading pair symbol, returned in the form of A_B
    name	        The name of the underlying index
    size	        Contract value, for example 0.0001 BTC
    volumePrecision	The precision of trading volume
    pricePrecision	The precision of price
    feeRate	Trading fees
    tradeMinLimit	Minimum trading unit
    currency	    Settlement currency
    asset	        Contract denomination asset
    """
    assert bingx.get_all_contracts() is not None


def test_get_latest_price():
    """
    Request:
        GET api/v1/market/getLatestPrice
    Parameters:
        symbol	String  BTC-USDT
    Response:
        {
            "code": 0,
            "msg": "",
            "data": {
              "tradePrice": "50000.18",
              "indexPrice": "50000.18",
              "fairPrice": "50000.18"
            }
        }
    tradePrice	float64	Trading Price
    indexPrice	float64	Index Price
    fairPrice	float64	Mark Price
    """
    assert bingx.get_latest_price("BTC-USDT") is not None


def test_get_market_depth():
    """
    Request:
        GET api/v1/market/getMarketDepth
    Parameters:
        symbol	String  BTC-USDT
        level   String  1 (Optional. Default is 5.)
    Response:
            {
                "code": 0,
                "msg": "",
                "data": {
                    "asks": [
                      {
                        "p": 5319.94,
                        "v": 0.05483456
                      }
                    ],
                    "bids": [
                      {
                        "p": 5319.93,
                        "v": 0.05483456
                      }
                    ],
                }
            }
    code	Int64	 For error messages, 0 means normal, 1 means error
    msg	    String	 Error message description
    asks	array	 Sell side depth
    bids	array	 Buy side depth
    p	    float64	 price
    v	    float64	 volume
    """
    assert get_market_depth("BTC-USDT", 1)


def test_get_latest_trade():
    """
    Request:
        GET api/v1/market/getMarketTrades
    Parameters:
        symbol	String  BTC-USDT
    Response:
         {
             "code": 0,
             "msg": "",
             "data": {
                 "trades": [
                     {
                         "time": "2018-04-25T15:00:51.999Z",
                         "makerSide": "Buy",
                         "price": 0.279563,
                         "volume": 100,
                     },
                     {
                         "time": "2018-04-25T15:00:51.000Z",
                         "makerSide": "Sell",
                         "price": 0.279563,
                         "volume": 300,
                     }
                 ]
             }
        }
    time	    data	Closing Time
    makerSide	String	Direction (Buy / Sell)
    price	    String	Closing Price
    volume	    String	Filled Amount
    """
    assert get_latest_trade("BTC-USDT")


def test_get_latest_funding():
    """
    Request:
        GET api/v1/market/getLatestFunding
    Parameters:
        symbol	String  BTC-USDT
    Response:
        {
            "code": 0,
            "msg": "",
            "data": {
              "fundingRate": "0.3000",
              "fairPrice": "182.90",
              "leftSeconds": "1024",
            }
        }
    fundingRate	 float64	Current Funding Rate
    fairPrice	 float64	Current Mark Price
    leftSeconds	 float64	Time left for the next settlement, in seconds
    """
    assert get_latest_funding("BTC-USDT")


def test_get_funding_history():
    """
    Request:
        GET api/v1/market/getHistoryFunding
    Parameters:
        symbol	String  BTC-USDT
    Response:
        {
             "code": 0,
             "msg": "",
             "data": {
                 "fundings": [
                     {
                         "historyId": "687",
                         "symbol": "ETH-USDT",
                         "fundingRate": "0.3000",
                         "fairPrice": "182.73",
                         "interval": "8",
                         "time": "2019-10-28T16:00:00.000Z"
                     },
                     {
                         "historyId": "686",
                         "symbol": "ETH-USDT",
                         "fundingRate": "0.3000",
                         "fairPrice": "182.90",
                         "interval": "8",
                         "time": "2019-10-28T15:00:00.000Z"
                     }
                 ]
             }
        }
    historyId	 String	 historyId
    fundingRate	 String	 Funding rate
    fairPrice	 String	 Mark Price
    interval	 String	 The funding rate settlement cycle, unit: hour
    time	     data	 Settlement Time
    """
    assert get_funding_history("BTC-USDT")


def test_get_kline_data():
    """
    Request:
        GET api/v1/market/getLatestKline
    Parameters:
        symbol	    String  BTC-USDT
        klineType	String  1D
    1	1min Kline
    3	3min Kline
    5	5min Kline
    15	15min Kline
    30	30min Kline
    60	1h Kline
    120	2h Kline
    240	4h Kline
    360	6h Kline
    720	12h Kline
    1D	1D Kline
    1W	1W Kline
    1M	1M Kline
    Response:
        {
            "code": 0,
            "msg": "",
            "data": {
                "kline": {
                    "ts": 1572253500000,
                    "open": 181.41,
                    "close": 181.54,
                    "high": 181.54,
                    "low": 181.39,
                    "volume": 281
                }
            }
        }
    open	float64	Open
    close	float64	Close
    high	float64	High
    low	    float64	Low
    volume	float64	Volume
    ts	    int64	The timestamp of K-Line，Unit: ms
    """
    assert get_kline_data("BTC-USDT", "1D")


def test_get_kline_history():
    """
    Request:
        GET api/v1/market/getHistoryKlines
    Parameters:
        symbol	    String	BTC-USDT
        klineType	String	1D
        startTs	    int64	Start timestamp, Unit: ms
        endTs	    int64	End timestamp, Unit: ms
    Response:
        {
            "code": 0,
            "msg": "",
            "data": {
                "klines": [
                    {
                        "ts": 1572253140000,
                        "open": 181.89,
                        "close": 181.97,
                        "high": 182.04,
                        "low": 181.89,
                        "volume": 2136
                    },
                    {
                        "ts": 1572253200000,
                        "open": 181.94,
                        "close": 181.72,
                        "high": 181.94,
                        "low": 181.72,
                        "volume": 965
                    }
                ]
            }
        }
    klines	array	 K-Line data
    open	float64	 Open
    close	float64	 Close
    high	float64	 High
    low	    float64	 Low
    volume	float64	 Volume
    ts	    int64	 The timestamp of K-Line, Unit: ms
    """
    assert get_kline_history("BTC-USDT", "1D", 1572253260000, 1573253260000)


def test_get_swap_open_positions():
    """
    Request:
        GET api/v1/market/getOpenPositions
    Parameters:
        symbol	String	BTC-USDT
    Response:
        {
            "code": 0,
            "msg": "",
            "data": {
              "volume": "10.00",
              "unit": "BTC",
            }
        }
    volume	float64	Volume of opened positions
    unit	string	The unit corresponding to the Volume of opened positions, CONT. - BTC, ETH, LINK, BCH, etc.
    """
    assert get_open_positions("BTC-USDT")


def test_get_tiker():
    """
    Request:
        GET api/v1/market/getTicker
    Parameters:
        symbol	String  BTC-USDT
    Response:
        {
            "code": 0,
            "msg": "",
            "data": {
              "symbol": "BTC-USDT",
              "priceChange": "10.00",
              "priceChangePercent": "10",
              "lastPrice": "5738.23",
              "lastVolume": "31.21",
              "highPrice": "5938.23",
              "lowPrice": "5238.23",
              "volume": "23211231.13",
              "dayVolume": "213124412412.47",
              "openPrice": "5828.32"
            }
        }
    symbol	            String	  Trading pair symbol
    priceChange	        String	  Price change, in USDT
    priceChangePercent	String	  Price change expressed as a percentage
    lastPrice	        String	  The price for the last trade
    lastVolume      	String	  The volume for the last trade
    highPrice	        String	  Highest price during 24h
    lowPrice	        String	  Lowest price during 24h
    volume	            String	  Volume during last 24h in base currency
    dayVolume	        String	  Volume during last 24h, in USDT
    openPrice	        String	  24h open price
    """
    assert get_tiker("BTC-USDT")


def test_():
    """
    Request:

    Parameters:

    Response:

    """
    assert null


def test_():
    """
    Request:

    Parameters:

    Response:

    """
    assert null


def test_():
    """
    Request:

    Parameters:

    Response:

    """
    assert null


def test_():
    """
    Request:

    Parameters:

    Response:

    """
    assert null


def test_():
    """
    Request:

    Parameters:

    Response:

    """
    assert null