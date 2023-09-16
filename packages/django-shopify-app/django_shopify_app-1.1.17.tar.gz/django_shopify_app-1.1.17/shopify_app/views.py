import json
import requests

from django.views import View
from django.urls import reverse
from django.conf import settings
from django.shortcuts import redirect, render, HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.utils.decorators import method_decorator

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException

import shopify

from .utils import (
    get_function_from_string,
    get_shop_model,
    webhook_request_is_valid,
    get_shop,
)
from .decorators import shopify_embed


class ShopAPIView(APIView):
    pass


def create_permission_url(shop_url, redirect_path="", redirect_path_name=""):
    shopify.Session.setup(
        api_key=settings.SHOPIFY_API_KEY, secret=settings.SHOPIFY_API_SECRET
    )

    api_version = "2022-07"
    state = ""

    if redirect_path_name:
        path = reverse(redirect_path_name)
    elif redirect_path:
        path = redirect_path

    redirect_uri = f"{settings.SHOPIFY_APP_HOST}{path}"
    scopes = settings.SHOPIFY_APP_SCOPES

    newSession = shopify.Session(shop_url, api_version)
    auth_url = newSession.create_permission_url(scopes, redirect_uri, state)
    return auth_url


class InitTokenRequestView(View):
    redirect_path_name = ""

    @method_decorator(xframe_options_exempt)
    @method_decorator(shopify_embed)
    def get(self, request, *args, **kwargs):
        shop_url = request.GET.get("shop")
        auth_url = create_permission_url(
            shop_url, redirect_path_name=self.redirect_path_name
        )

        if request.GET.get("embedded"):
            context = {
                "api_key": settings.SHOPIFY_API_KEY,
                "host": request.GET.get("host"),
                "redirect": auth_url,
            }
            return render(request, "shopify_app/index.html", context=context)
        else:
            return redirect(auth_url)


def request_personal_access_token(shop, client_id, client_secret, authorization_code):
    response = requests.post(
        (
            f"https://{shop}/admin/oauth/access_token"
            f"?client_id={client_id}&client_secret={client_secret}&"
            f"code={authorization_code}"
        )
    )
    print(response.text)
    if response.status_code != 200:
        raise Exception("Could not request access token")

    return response.json()


class EndTokenRequestView(View):
    redirect_path_name = ""

    def get(self, request, *args, **kwargs):
        shop_url = request.GET.get("shop")

        shopify.Session.setup(
            api_key=settings.SHOPIFY_API_KEY, secret=settings.SHOPIFY_API_SECRET
        )

        if not shopify.Session.validate_params(request.GET.dict()):
            raise Exception("Invalid HMAC: Possibly malicious login")

        data = request_personal_access_token(
            shop_url,
            settings.SHOPIFY_API_KEY,
            settings.SHOPIFY_API_SECRET,
            request.GET.get("code"),
        )

        Shop = get_shop_model()
        shop_record = Shop.objects.get_or_create(shopify_domain=shop_url)[0]

        if data.get("associated_user"):
            shop_record.on_user_login(data["associated_user"], request=request)

            host = settings.SHOPIFY_APP_HOST
            path = reverse(self.redirect_path_name)
            query = request.META["QUERY_STRING"]

            return redirect(f"{host}{path}?{query}")
        else:
            access_token = data.pop("access_token")

        installed = bool(not shop_record.shopify_token and access_token)

        shop_record.shopify_token = access_token
        shop_record.access_scopes = data["scope"]

        shop_record.save()

        if installed:
            shop_record.installed(request=request)

        auth_url = create_permission_url(shop_url, redirect_path=request.path)
        return redirect(f"{auth_url}&grant_options[]=per-user")


class WebhookAuthenticationFailed(APIException):
    status_code = 401
    default_detail = "authentication failed"


class MandatoryWebhooksView(APIView):
    topic = None

    def post(self, request, *args, **kwargs):
        domain = request.META["HTTP_X_SHOPIFY_SHOP_DOMAIN"]
        hmac_header = self.request.META.get("HTTP_X_SHOPIFY_HMAC_SHA256")

        try:
            shop = get_shop(domain)
        except:
            raise WebhookAuthenticationFailed()

        if not webhook_request_is_valid(shop, hmac_header, request.body):
            raise WebhookAuthenticationFailed()

        func = get_function_from_string(settings.SHOPIFY_GDPR_WEBHOOK_CALLBACK)
        func(shop, self.topic, request.data, attributes={})

        return Response(status=200)


class WebhooksView(APIView):
    def post(self, request, *args, **kwargs):
        meta = request.META
        shop = get_shop(meta["HTTP_X_SHOPIFY_SHOP_DOMAIN"])
        hmac = meta["HTTP_X_SHOPIFY_HMAC_SHA256"]
        webhook_topic = meta["HTTP_X_SHOPIFY_TOPIC"]
        api_version = meta["HTTP_X_SHOPIFY_API_VERSION"]
        data = request.body

        if webhook_request_is_valid(shop, hmac, data):
            callback_path = settings.SHOPIFY_WEBHOOK_CALLBACK
            data = json.loads(data.decode("utf-8"))
            func = get_function_from_string(callback_path)
            attributes = {
                "api_version": api_version,
            }
            func(shop, webhook_topic, data, attributes=attributes)
            return Response(status=200)
        else:
            raise WebhookAuthenticationFailed()
