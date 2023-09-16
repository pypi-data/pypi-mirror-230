import json
import base64
from functools import cached_property

from django.db import models
from django.apps import apps
from django.conf import settings

import shopify
from shopify import Session

from .services.webhooks import update_shop_webhooks


class ShopBase(models.Model):
    shopify_domain = models.CharField(max_length=50, default="")
    shopify_token = models.CharField(max_length=150, default="", blank=True, null=True)
    access_scopes = models.CharField(max_length=250, default="")

    @cached_property
    def shopify(self):
        return shopify

    @property
    def shopify_app_api_secret(self):
        return apps.get_app_config("shopify_app").SHOPIFY_API_SECRET

    @property
    def shopify_session(self):
        api_version = apps.get_app_config("shopify_app").SHOPIFY_API_VERSION
        shopify_domain = self.shopify_domain
        return Session.temp(shopify_domain, api_version, self.shopify_token)

    def installed(self, request=None):
        pass

    def update_webhooks(self):
        update_shop_webhooks(self)

    def graph(self, operation_name, variables, operations_document):
        with self.shopify_session:
            result = shopify.GraphQL().execute(
                query=operations_document,
                variables=variables,
                operation_name=operation_name,
            )

        result = json.loads(result)
        return result

    @cached_property
    def host(self):
        admin_url = f"{self.shopify_domain}/admin"
        return base64.b64encode(admin_url.encode()).decode()

    def on_user_login(self, user_data, request=None):
        print(user_data)

    class Meta:
        abstract = True
