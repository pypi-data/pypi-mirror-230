from django.conf import settings

from django.apps import apps
from django.urls import reverse


def update_shop_webhooks(shop):
    config = apps.get_app_config("shopify_app")

    with shop.shopify_session:

        if config.use_pubsub:
            address = "pubsub://{}:{}".format(
                config.GOOGLE_PUBSUB_PROJECT_ID,
                config.GOOGLE_PUBSUB_TOPIC_ID,
            )
        else:
            path = reverse("shopify_app:webhooks")
            address = f"{config.WEBHOOK_HOST}{path}"

        for topic in settings.SHOPIFY_WEBHOOK_TOPICS:
            webhooks = shop.shopify.Webhook.find(topic=topic)

            if len(webhooks):
                webhook = webhooks[0]
                webhook.address = address
                webhook.save()

            else:
                webhook = shop.shopify.Webhook.create({
                    "topic": topic,
                    "address": address,
                    "format": "json"
                })

        print(shop.shopify.Webhook.find())

        for created_webhook in shop.shopify.Webhook.find():
            if created_webhook.topic not in settings.SHOPIFY_WEBHOOK_TOPICS:
                created_webhook.destroy()
