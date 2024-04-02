from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from bp_bot import TradeBot

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"
socketio = SocketIO(app)

# 表单默认值
default_form_data = {
    "API_KEY": "",
    "API_SECRET": "",
    "WISH_VOLUME": 100,
    "ITER_NUM": 2,
    "TRADE_TOKEN": "WEN",
    "TRADE_PAIR": "WEN_USDC",
    "PAIR_ACCURACY": 8,
    "MIN_USDC": 20,
    "MIN_PAIR": 10000,
}

# 保存表单数据
form_data = default_form_data.copy()

# 线程控制标志
is_running = False


@socketio.on("submit_form")
def handle_form_submit(form_data):
    print(f"Received form data: {form_data}")

    def logger(x):
        print(x)
        socketio.emit("log_update", x)
        socketio.sleep(1)

    global is_running
    is_running = True
    # while is_running:
    #     socketio.emit("log_update", "1")
    #     socketio.sleep(2)
    bot = TradeBot(form_data, logger)
    for i in range(bot.ITER_NUM):
        if not is_running:
            logger("停止")
            break
        logger(f"第{i}轮")
        bot.one_iter()


@app.route("/")
def index():
    return render_template("index.html", form_data=form_data)


@socketio.on("stop_bot")
def handle_stop_bot():
    global is_running
    is_running = False


if __name__ == "__main__":
    socketio.run(app, port=5001, debug=True)
