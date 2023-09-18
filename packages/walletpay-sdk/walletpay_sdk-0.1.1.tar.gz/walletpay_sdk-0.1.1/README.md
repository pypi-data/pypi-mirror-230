# Wallet Pay Python API
https://docs.wallet.tg/pay/

## Installation
It's not on pypi yet :(  
You can try to install it like so:  
`pip install git+https://github.com/pypchuk/wallet_pay.git#egg=wallet_pay`  
Or just clone it and run poetry install  

## Requirements
1. Python >= 3.11

## Running tests
1. Add WP_TEST_KEY environment variable with your API key
2. From the root dir run
```
python -m pytest tests
```

## Running examples
1. Clone repo
2. Run `poetry install --group examples`
3. Add env vars:  
3.1 Add WP_TEST_KEY with your API key  
3.2 (FOR bot.py) Add WP_BOT_TOKEN with bot token bound to your api  
4. Go to examples folder and run them like regular python scripts  

### Note about webhooks example
WARNING! For development purposes only!
To run webhook example you need dedicated IP address
You can use ngrok to test your application:
1. Download ngrok and log in
2. Run `ngrok http 80`
3. Copy your temporary IP address
4. Paste it in your merchant settings
5. !AFTER DEVELOPMENT DON'T FORGET TO REMOVE ADDRESS IN WALLETPAY WEBHOOK SETTINGS PROVIDED FROM NGROK!