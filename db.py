import firebase_admin
from firebase_admin import firestore, credentials

cred = credentials.Certificate("firebase.conf.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

docs = db.collection(u"service-workers")


def addSubscription(subscription_json):
    docs.add({u'subscription': subscription_json})
    return 'Successfully Added'


def deleteSubscription(subscription_json):
    docs.add({u'subscription': subscription_json})
    return 'Successfully Delete'