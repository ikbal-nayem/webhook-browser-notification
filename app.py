import re
from flask import Flask, request, render_template, jsonify, redirect
import datetime
from db import addUserSubscriptionDevice, getAllSubscribers, addService, getServiceList
from firebase_admin import auth
from pushNotificationHandler import sendBulkNotification
from utils import authenticate

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('application.cfg.py')
app.app_context().push()


@app.route('/auth', methods=['GET', 'POST'])
def authentication():
    if request.method == 'GET':
        return render_template('auth.html', title='Authentication', cid=app.config['VAPID_GOOGLE_CLIENT_ID'])

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
        return redirect('/')

    except ValueError as e:
        return jsonify({'error': str(e)}), 401


@app.route('/sign-up', methods=['POST'])
def sign_up():
    email = request.get_json().get('email')
    password = request.get_json().get('password')

    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400
    try:
        user = auth.create_user(email=email, password=password, disabled=True)
        return jsonify({'message': 'User created successfully. You will be able to login after verification process.', 'uid': user.uid}), 201
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400


@app.route('/sign-in', methods=['POST'])
def sign_in():
    email = request.get_json().get('email')
    password = request.get_json().get('password')

    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400
    try:
        user = auth.get_user_by_email(email)
        print(dir(user))
        if user.disabled == True:
            return jsonify({'error': 'Please contact to admin for verification'}), 400
        return redirect('/')
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400


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
