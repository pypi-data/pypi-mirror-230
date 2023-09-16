import json
import logging

from google.auth import jwt
from google.cloud import pubsub_v1

from django.apps import AppConfig
from django.conf import settings
from django.core.management import BaseCommand, CommandError
from django.utils import autoreload

from ...utils import (
    get_function_from_string, get_shop, webhook_request_is_valid
)

logger = logging.getLogger(__name__)


def pubsub_callback(message):

    callback_path = settings.SHOPIFY_WEBHOOK_CALLBACK

    try:
        shop = get_shop(message.attributes['X-Shopify-Shop-Domain'])
        hmac = message.attributes['X-Shopify-Hmac-SHA256']

        if webhook_request_is_valid(shop, hmac, message.data):

            data = json.loads(message.data.decode('utf-8'))
            webhook_topic = message.attributes['X-Shopify-Topic']
            func = get_function_from_string(callback_path)
            attributes = {
                "api_version": message.attributes['X-Shopify-API-Version'],
            }
            func(shop, webhook_topic, data, attributes=attributes)

    except Exception as e:
        logger.error(str(e))

    message.ack()


def subscribe_to_pubsub():
    subscription_name = 'projects/{project_id}/subscriptions/{sub}'.format(
        project_id=settings.SHOPIFY_GOOGLE_PUBSUB_PROJECT_ID,
        sub=settings.SHOPIFY_GOOGLE_PUBSUB_SUB_NAME,
    )
    service_account_info = json.loads(
        settings.SHOPIFY_GOOGLE_PUBSUB_SERVICE_ACCOUNT_STRING,
    )

    audience = "https://pubsub.googleapis.com/google.pubsub.v1.Subscriber"

    credentials = jwt.Credentials.from_service_account_info(
        service_account_info, audience=audience
    )

    with pubsub_v1.SubscriberClient(credentials=credentials) as subscriber:
        future = subscriber.subscribe(subscription_name, pubsub_callback)
        try:
            print('pubsub running')
            future.result()
        except KeyboardInterrupt:
            future.cancel()


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--autoreload', action='store_true',
            help='Auto reload after code update'
        )

    def execute(self, *args, **options):

        if options['autoreload']:
            autoreload.run_with_reloader(
                subscribe_to_pubsub
            )
        else:
            subscribe_to_pubsub()
