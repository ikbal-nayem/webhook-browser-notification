from flask import Flask, request, render_template, jsonify
from db import addUserSubscriptionDevice

app = Flask(__name__, instance_relative_config=True)

app.config.from_pyfile('application.cfg.py')
app.app_context().push()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/service-worker/subscription", methods=["POST"])
def create_push_subscription():
    json_data = request.get_json()
    status = addUserSubscriptionDevice(json_data['user'], json_data['subscription_json'])
    return jsonify(status)


@app.route("/webhook", methods=["POST"])
def receive_webhook():
    data = request.get_json()
    print(f"Received webhook data: {data}")
    return "Webhook received successfully!", 200


if __name__ == "__main__":
    app.run(debug=True)

# Current service worker https://fkh9sv-5000.csb.app/
