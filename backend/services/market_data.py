import requests
from flask import current_app

def get_stock_quote(symbol):
    """Fetch real-time quote from Alpha Vantage"""
    api_key = current_app.config['ALPHA_VANTAGE_KEY']
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}'
    try:
        response = requests.get(url)
        data = response.json()
        if 'Global Quote' in data and data['Global Quote']:
            quote = data['Global Quote']
            return {
                'symbol': quote.get('01. symbol'),
                'price': float(quote.get('05. price', 0)),
                'change': float(quote.get('09. change', 0)),
                'change_percent': quote.get('10. change percent', '0%').replace('%', '')
            }
    except Exception as e:
        print(f"Error fetching quote: {e}")
    return None

def get_historical_data(symbol, interval='daily'):
    """Fetch historical daily prices (last 100 days)"""
    api_key = current_app.config['ALPHA_VANTAGE_KEY']
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}'
    try:
        response = requests.get(url)
        data = response.json()
        if 'Time Series (Daily)' in data:
            ts = data['Time Series (Daily)']
            # Return last 30 days
            result = []
            for date, values in list(ts.items())[:30]:
                result.append({
                    'date': date,
                    'open': float(values['1. open']),
                    'high': float(values['2. high']),
                    'low': float(values['3. low']),
                    'close': float(values['4. close']),
                    'volume': int(values['5. volume'])
                })
            return result
    except Exception as e:
        print(f"Error fetching historical: {e}")
    return []
