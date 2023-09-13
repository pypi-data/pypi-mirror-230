from fast_tradier.utils.YFinanceQuoteProvider import YFinanceQuoteProvider
from pathlib import Path

price_pattern_file_name = 'yahoo-price-pattern'
pattern_file = Path(Path(__file__).resolve().parent.parent, 'utils', price_pattern_file_name)
print('pattern_file_path: ', pattern_file)

yfin_quote_provider = YFinanceQuoteProvider()
ticker = ['^GSPC', 'AAPL', 'MSFT']
for t in ticker:
    price = yfin_quote_provider.get_price(t)
    print(f'ticker {t} price: {price}')