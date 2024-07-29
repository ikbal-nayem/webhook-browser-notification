import json
import firebase_admin
from firebase_admin import firestore, credentials
from pushNotificationHandler import sendSingleNotification

cred = credentials.Certificate("./instance/firebase.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

users = db.collection("users")
services = db.collection("services")


def getUserDevices(user) -> list:
    d = users.document(user).get().to_dict()
    return d.get('devices') if d else []


def addUserSubscriptionDevice(user, subscription_str):
    subscription_json = json.loads(subscription_str) if type(
        subscription_str) is str else subscription_str
    ud = getUserDevices(user)
    if ud and len(ud) > 0:
        for d in ud:
            if d['endpoint'] == subscription_json['endpoint']:
                sendSingleNotification(subscription_json, {
                    'title': 'Already Subscribed', 'body': 'You Are Already Subscribed to the Service', 'tag': 'add-subscriber'})
                return {'status': 'success', 'message': 'Already Subscribed'}

    if ud and len(ud) > 0:
        users.document(user).update(
            {'devices': firestore.ArrayUnion([subscription_json])})
    else:
        users.document(user).set({'devices': [subscription_json]}, merge=True)
    sendSingleNotification(subscription_json, {
        'title': 'Successfully Saved', 'body': 'Notification service is ready to use. Please select services below to get notifications.', 'tag': 'add-subscriber'})
    return {'status': 'success', 'message': 'Successfully Saved'}


def getAllSubscribers():
    s_list = []
    for u in users.list_documents():
        device = u.get().to_dict()
        s_list.extend(device.get('devices') if device else [])
    return s_list


def getServiceBasedSubscribers(service, env):
    subscribed_users = services.document(service).get().to_dict()
    if not subscribed_users:
        return []
    devices = []
    for user in subscribed_users.get(env):
        devices.extend(getUserDevices(user))
    return devices


def getUserSubscription(user):
    id = user.get('email')
    li = []
    for s in services.list_documents():
        service_data = s.get().to_dict()
        for e in list(service_data.keys()):
            if id in service_data[e]:
                li.append(f'{e}_{s.id}')
    return li


def setUserSubscription(user, services_list: list, prev_subscriptions: list):
    for cs in prev_subscriptions:
        if cs not in services_list:
            services.document(cs.split('_')[1]).update({
                cs.split('_')[0]: firestore.ArrayRemove([user.get('email')])
            })
    for s in services_list:
        if s not in prev_subscriptions:
            services.document(s.split('_')[1]).update({
                s.split('_')[0]: firestore.ArrayUnion([user.get('email')])
            })


def addService(service):
    return services.document(service).set({
        'stage': [],
        'training': [],
        'production': [],
    }, merge=True)


def getServiceList():
    return [s.id for s in services.list_documents()]
