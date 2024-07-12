from flask import Flask, request, render_template, jsonify
from db import addSubscription

app = Flask(__name__, instance_relative_config=True)

app.config.from_pyfile('application.cfg.py')
app.app_context().push()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/service-worker/subscriptions", methods=["POST"])
def create_push_subscription():
    json_data = request.get_json()
    addSubscription(json_data['subscription_json'])
    return jsonify({
        "status": "Successfully Saved!",
    })


@app.route("/webhook", methods=["POST"])
def receive_webhook():
    # Get data sent by the webhook
    data = request.get_json()

    # Process the data (e.g., print, save to database)
    print(f"Received webhook data: {data}")

    # You can return a response to the webhook sender if needed
    return "Webhook received successfully!", 200


if __name__ == "__main__":
    app.run(debug=True)


# Current service worker https://fkh9sv-5000.csb.app/
