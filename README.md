# Run
```shell

make install
python app.py

# open browser: http://127.0.0.1:5001/
```

# Form 
```shell

API_KEY: '' #填入你的api key
API_SECRET: '' #填入你的api secret
WISH_VOLUME: '500' # 每轮的目标交易量
ITER_NUM: '2' # 一共多少轮，所以，总的交易量 ITER_NUM * WISH_VOLUME
TRADE_TOKEN: 'SOL'
TRADE_PAIR: 'SOL_USDC'
PAIR_ACCURACY: '2' # 交易对价格精度
MIN_USDC: '200' # 每次交易 usdc 的量，越小磨损越小，但是达到目标交易量越慢
MIN_PAIR: '100' # 每次交易 目标 token 的量，越小磨损越小，但是达到目标交易量越慢
```

# Screen
![image](https://github.com/sing1ee/backpack-bot-py/assets/1057882/fa679ff0-26da-4c2e-9997-1b65f1cfa446)
