# LIVE  python_strategies

## Steps to install Strategy Library for LIVE


```python

pip install breeze_strategies==1.0.14

```

## Updating Library

```python

pip install --upgrade breeze_strategies

```

## code usage

```python

#Import the library
from breeze_strategies import Strategies

#Configure the strategy using API Keys and set stoploss/takeprofit level.
obj = Strategies(app_key = "your app key",
                 secret_key = "your secret key",
                 api_session = "your api session",
                 max_profit = "your max profit",
                 max_loss = "your max loss")

#Execute the strategy
obj.straddle(strategy_type = "long",
             stock_code = "NIFTY",
             strike_price = "18700",
             quantity = "50",
             expiry_date = "2023-06-29T06:00:00.000Z")

#Execute the strangle strategy
obj.strangle(strike_price_call = "18700",strike_price_put = "18300", strategy_type = "long",stock_code = "NIFTY", quantity = "50", expiry_date = "2023-06-29T06:00:00.000Z"):

#Execute Single Leg
obj.single_leg(right = "Call", strategy_type = "short",stock_code = "NIFTY", strike_price = "18700", quantity = "50", expiry_date = "2023-06-29T06:00:00.000Z")


#SquareOff existing positions and exit the strategy for straddle
obj.stop() 

#SquareOff existing positions and exit the strategy for strangle
obj.stop(is_strangle = True) 

#SquareOff existing positions and exit the strategy In case of single_leg pass single_leg flag as True as mentioned below
obj.stop(single_leg = True)


#Generate Profit & Loss report (this method will work for both straddle and strangle)
obj.get_pnl()

#Execute Butterfly
obj.butterfly(right = "Call",strategy_type = "short",stock_code = "NIFTY",spread = "100", strike_price = "18700", quantity = "50", expiry_date = "2023-06-29T06:00:00.000Z")

# Generate Profit & Loss Report
obj.get_pnl(is_butterfly = True)

# square off existing positions and exit strategy for butterfly
obj.stop(is_butterfly = True)
```

