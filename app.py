import json
from flask import Flask, request, render_template, jsonify, redirect, session
import datetime
from db import addUserSubscriptionDevice, getServiceBasedSubscribers, getUserDevices, addService, getServiceList, setUserSubscription, getUserSubscription
from firebase_admin import auth
from pushNotificationHandler import sendBulkNotification

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('application.cfg.py')
app.secret_key = app.config['APP_SECRET_KEY']
app.app_context().push()


@app.route('/auth', methods=['GET', 'POST'])
def authentication():
    user = session.get('user')
    if user:
        return redirect('/')

    if request.method == 'GET':
        return render_template('auth.html', title='Authentication', cid=app.config['GOOGLE_CLIENT_ID'])

    id_token = request.get_json().get('idToken')
    user = request.get_json().get('user')
    if not id_token:
        return jsonify({'error': 'Missing ID token'}), 400

    try:
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
    name = request.get_json().get('name')

    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400
    try:
        user = auth.create_user(
            email=email, password=password, display_name=name, disabled=True)
        return jsonify({'message': 'User created successfully. You will be able to login after verification process.', 'uid': user.uid}), 201
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400


@app.route('/sign-in', methods=['POST'])
def sign_in():
    user = request.json
    if not user:
        return jsonify({'error': 'No user provided'}), 400
    session['user'] = user
    return jsonify({'success': 'User signed in successfully'}), 200


@app.route("/")
def home():
    user = session.get('user')
    if not user:
        return redirect('/auth')
    services = getServiceList()
    user_subscriptions = getUserSubscription(user)
    return render_template("index.html", title="Deployment Status", user=user, services=services, user_subscriptions=user_subscriptions)


@app.route("/service-worker/subscription", methods=["POST"])
def create_push_subscription():
    json_data = request.get_json()
    status = addUserSubscriptionDevice(
        json_data['user'], json_data['subscription_json'])
    return jsonify(status), 200


@app.route("/substribe", methods=["POST"])
def substribe():
    req_json = request.get_json()
    data = req_json.get('data')
    prev_subscriptions = req_json.get('prev_subscriptions')
    user = session.get('user')
    setUserSubscription(user, data, prev_subscriptions)
    return jsonify({'message': "Successfully saved"}), 200


@app.route("/webhook", methods=["POST"])
def receive_webhook():
    data = request.get_json()
    print(f"Received webhook data: {data}")
    addService(data.get('service'))
    substribers = getServiceBasedSubscribers(
        data.get('service'), data.get('env'))
    notification = {
        'title': f"{data.get('service')} ({data.get('env')})", 'body': data.get('status')}
    sendBulkNotification(substribers, notification)
    return "Webhook received successfully!", 200


if __name__ == "__main__":
    app.run(debug=True)
