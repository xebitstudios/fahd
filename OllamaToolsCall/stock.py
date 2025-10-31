import ollama
import yfinance as yf
from typing import Dict, Any, Callable

def get_stock_price(symbol: str) -> float:
    ticker = yf.Ticker(symbol)
    price_attrs = ['regularMarketPrice', 'currentPrice', 'price']
    
    for attr in price_attrs:
        if attr in ticker.info and ticker.info[attr] is not None:
            return ticker.info[attr]
            
    fast_info = ticker.fast_info
    if hasattr(fast_info, 'last_price') and fast_info.last_price is not None:
        return fast_info.last_price
        
    raise Exception("Could not find valid price data")

# Manual tool definition
get_stock_price_tool = {
    'type': 'function',
    'function': {
        'name': 'get_stock_price',
        'description': 'Get the current stock price for any symbol',
        'parameters': {
            'type': 'object',
            'required': ['symbol'],
            'properties': {
                'symbol': {'type': 'string', 'description': 'The stock symbol (e.g., AAPL, GOOGL)'},
            },
        },
    },
}

prompt = 'What is the current stock price of Apple?'
print('Prompt:', prompt)

available_functions: Dict[str, Callable] = {
    'get_stock_price': get_stock_price,
}

response = ollama.chat(
    'llama3.2',
    messages=[{'role': 'user', 'content': prompt}],
    tools=[get_stock_price_tool],
)

if response.message.tool_calls:
    for tool in response.message.tool_calls:
        if function_to_call := available_functions.get(tool.function.name):
            print('Calling function:', tool.function.name)
            print('Arguments:', tool.function.arguments)
            print('Function output:', function_to_call(**tool.function.arguments))
        else:
            print('Function', tool.function.name, 'not found')