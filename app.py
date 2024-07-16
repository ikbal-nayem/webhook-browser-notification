from flask import Flask, request, render_template, jsonify
from firebase_admin import auth
import datetime
from db import addUserSubscriptionDevice, getAllSubscribers, addService, getServiceList
from pushNotificationHandler import sendBulkNotification
from utils import authenticate

app = Flask(__name__, instance_relative_config=True)

app.config.from_pyfile('application.cfg.py')
app.app_context().push()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth.html', title='Authentication')

    id_token = request.get_json().get('idToken')
    if not id_token:
        return jsonify({'error': 'Missing ID token'}), 400

    try:
        # Verify the ID token
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        # ... (You can access other user information from decoded_token)

        # Create a session cookie (optional, but recommended for secure sessions)
        expires_in = datetime.timedelta(days=1)
        session_cookie = auth.create_session_cookie(
            id_token, expires_in=expires_in)
        response = jsonify({'status': 'success'})
        response.set_cookie('session', session_cookie,
                            httponly=True, secure=True)
        return redirect(url_for('/'))

    except ValueError as e:
        return jsonify({'error': str(e)}), 401


@app.route("/")
@authenticate
def home():
    services = getServiceList()
    return render_template("index.html", title="Deployment Status", services=services)


@app.route("/service-worker/subscription", methods=["POST"])
@authenticate
def create_push_subscription():
    json_data = request.get_json()
    status = addUserSubscriptionDevice(
        json_data['user'], json_data['subscription_json'])
    return jsonify(status)


@app.route("/webhook", methods=["POST"])
def receive_webhook():
    data = request.get_json()
    print(f"Received webhook data: {data}")
    addService(data['service'])
    sendBulkNotification(getAllSubscribers(), {
                         'title': f"{data['service']} ({data['env']})", 'body': data['status']})
    return "Webhook received successfully!", 200


if __name__ == "__main__":
    app.run(debug=True)

# Current service worker https://fkh9sv-5000.csb.app/
