import requests
import pandas as pd
import time

import hashlib

import ta
import hmac

#Remember to remove before commit
api_key = ''
api_secret = ''
base_url = 'https://fapi.bitunix.com'

symbol = 'BTCUSDT'
interval = '15m' 
risk_ratio = 1.5 
sleep_time = 60  

# Private endpoints
def create_signature(params, secret):
    sorted_params = sorted(params.items())
    query_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
    return hmac.new(secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

# kline data
def fetch_ohlcv():
    url = f"{base_url}/api/v1/futures/market/kline"
    params = {
        'symbol': symbol,
        'interval': interval,
        'limit': 100
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Ensure no HTTP error
    except Exception as e:
        raise Exception(f"HTTP error fetching Kline data: {e}")

    
    data = response.json()

    if data.get('code') != 0 or 'data' not in data:
        raise Exception(f"Failed to fetch kline data: {data}")

    df = pd.DataFrame(data['data'])
    # Convert timestamp and columns

    if 'ts' in df.columns:
        df['timestamp'] = pd.to_datetime(df['ts'], unit='ms')
    elif 'time' in df.columns:
        df['timestamp'] = pd.to_datetime(df['time'].astype('int64'), unit='ms')
    else:
        raise Exception("Timestamp column not found in API response. Columns: " + str(df.columns))

    df = df.rename(columns={
        'open': 'open',
        'high': 'high',
        'low': 'low',
        'close': 'close',
        'quoteVol': 'volume'  # base volume
    })

    num_cols = ['open', 'high', 'low', 'close', 'volume']
    df[num_cols] = df[num_cols].astype(float)

    return df


def apply_indicators(df):
    # VWAP uses base volume
    df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
    df['vwap'] = (df['typical_price'] * df['volume']).cumsum() / df['volume'].cumsum()
    df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=5)
    stoch = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close'], window=5, smooth_window=3)
    df['stoch_k'] = stoch.stoch()
    df['stoch_d'] = stoch.stoch_signal()
    return df


def generate_signal(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]

    # Long setup
    if (
        last['close'] > last['vwap'] and
        prev['stoch_k'] < 20 and last['stoch_k'] > 20 and
        last['stoch_k'] > last['stoch_d'] and
        last['atr'] > prev['atr']
    ):
        return 'buy', last['close'], last['atr']

    # Short setup
    if (
        last['close'] < last['vwap'] and
        prev['stoch_k'] > 80 and last['stoch_k'] < 80 and
        last['stoch_k'] < last['stoch_d'] and
        last['atr'] > prev['atr']
    ):
        return 'sell', last['close'], last['atr']

    return None, None, None


def place_order(signal, entry_price, atr):
    sl = entry_price - risk_ratio * atr if signal == 'buy' else entry_price + risk_ratio * atr
    tp = entry_price + 2 * atr if signal == 'buy' else entry_price - 2 * atr

    print(f"\\Signal: {signal.upper()}")
    print(f"Entry Price: {entry_price:.2f}")
    print(f"Stop Loss:  {sl:.2f}")
    print(f"Take Profit: {tp:.2f}\n")

#Uncomment when actually running, not for testing
    # url = f"{base_url}/api/spot/v1/trade/order"
    # timestamp = int(time.time() * 1000)
    # params = {
    #     'symbol': symbol,
    #     'side': 'buy' if signal == 'buy' else 'sell',
    #     'type': 'market',
    #     'quantity': 0.001,
    #     'timestamp': timestamp,
    # }
    # signature = create_signature(params, api_secret)
    # headers = {
    #     'X-BX-APIKEY': api_key,
    #     'X-BX-SIGNATURE': signature
    # }
    # response = requests.post(url, data=params, headers=headers)
    # print("Order Response:", response.json())


def run_strategy():
    print("Starting VWAP + ATR + Stochastic Strategy on Bitunix...\n")
    while True:
        try:
            df = fetch_ohlcv()
            df = apply_indicators(df)
            signal, entry_price, atr = generate_signal(df)

            if signal:
                place_order(signal, entry_price, atr)
            else:
                print("No trade signal this cycle.")

            time.sleep(sleep_time)

        except Exception as e:
            print("Error:", e)
            time.sleep(60)

if __name__ == "__main__":
    run_strategy()
