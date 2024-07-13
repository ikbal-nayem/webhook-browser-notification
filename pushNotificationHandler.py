from pywebpush import webpush, WebPushException
import json
from flask import current_app

def triggerNotification(subscription_json, title, body, tag=None):
    try:
        response = webpush(
            subscription_info=subscription_json,
            data=json.dumps({"title": title, "body": body, "tag": tag}),
            vapid_private_key=current_app.config["VAPID_PRIVATE_KEY"],
            vapid_claims={
                "sub": "mailto:{}".format(
                    current_app.config["VAPID_CLAIM_EMAIL"])
            }
        )
        return response
    except WebPushException as ex:
        if ex.response and ex.response.json():
            extra = ex.response.json()
            print("Remote service replied with a {}:{}, {}",
                  extra.code,
                  extra.errno,
                  extra.message
                  )
        return False

def sendBulkNotification(subscriptions, options:dict):
    for subscription in subscriptions:
        triggerNotification(subscription, options['title'], options['body'], options['tag'])

def sendSingleNotification(subscription, options:dict):
    triggerNotification(subscription, options['title'], options['body'], options['tag'])