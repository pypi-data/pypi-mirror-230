import base64
import hashlib
import hmac
import importlib
from django.apps import apps
from django.conf import settings


def get_shop_model():
    Model = apps.get_model(settings.SHOPIFY_SHOP_MODEL)
    return Model


def get_shop(shopify_domain):
    Model = get_shop_model()
    shop = Model.objects.get(shopify_domain=shopify_domain)
    return shop


def get_function_from_string(string):
    func_name = string.rsplit('.')[-1]
    location = string.replace(f'.{func_name}', "")
    module = importlib.import_module(location)
    if not hasattr(module, func_name):
        raise AttributeError(
            f"Module {module} does not have function {func_name}"
        )
    func = getattr(module, func_name)
    return func


def webhook_request_is_valid(shop, received_hmac, message):

    secret = shop.shopify_app_api_secret.encode('utf-8')
    digest = hmac.new(secret, message, hashlib.sha256).digest()
    computed_hmac = base64.b64encode(digest)
    received_hmac = received_hmac.encode('utf-8')
    is_valid = hmac.compare_digest(computed_hmac, received_hmac)
    return is_valid
