# Venezuela Dollar Price

`venezuela_dollar_price` is a Python library created to retrieve the current dollar price in Venezuela. It is simple to use and requires minimal setup.

## Features

- Get the latest dollar price in Venezuelan Bolivars.
- Retrieve historical dollar prices.
- User-friendly and intuitive to use.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install `venezuela-dollar-price`.

```bash
pip install venezuela-dollar-price
```

## Usage

```python
import venezuela_dollar_price as vdp

# get the latest dollar price (BCV)
latest_price = vdp.get_latest_price("bcv")
print(latest_price.rate)

# get the latest dollar price ("binance")
latest_price = vdp.get_latest_price("binance")
print(latest_price.rate)

# get the latest dollar price ("parallel")
latest_price = vdp.get_latest_price("prom_epv")
print(latest_price.rate)
# get historical prices of the dollar (BCV)
# Note: only works for the BCV and EPV
# minimum date: 2020-12-14
historical_prices = vdp.get_historical_prices(start_date="2020-01-01", end_date="2023-01-31")
for price in historical_prices:
    print(price.date, price.rate)
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
