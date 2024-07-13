import json
import firebase_admin
from firebase_admin import firestore, credentials
from pushNotificationHandler import sendSingleNotification

cred = credentials.Certificate("firebase.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

users = db.collection("users")
services = db.collection("services")


def getUserSubscriptionDevices(user) -> list | None:
    devices = users.document(user).collection('devices').get()
    return [d.to_dict() for d in devices] if devices else None


def addUserSubscriptionDevice(user, subscription_str):
    subscription_json = json.loads(subscription_str) if type(subscription_str) is str else subscription_str
    ud = getUserSubscriptionDevices(user)
    if ud and len(ud) > 0:
        for d in ud:
            if d['endpoint'] == subscription_json['endpoint']:
                sendSingleNotification(subscription_json, {'title': 'Already Subscribed', 'body': 'You Are Already Subscribed to the Service'})
                return {'status': 'success', 'message': 'Already Subscribed'}
    users.document(user).collection('devices').add({**subscription_json})
    sendSingleNotification(subscription_json, {'title':'Successfully Saved', 'body': 'You Have Successfully Subscribed to the Service'})
    return {'status': 'success', 'message': 'Successfully Saved'}


# def deleteSubscription(doc):
#     users.document(doc).delete()
#     return 'Successfully Delete'


def getAllSubscribers():
    s_list = []
    for s in [u.collection('devices').get() for u in users.list_documents()]:
        for d in s:
            s_list.append(d.to_dict())
    return s_list


# if __name__ == "__main__":
#     s = getAllSubscribers()
#     print(s)