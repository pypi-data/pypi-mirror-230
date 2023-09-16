

from django.apps import apps
from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import redirect
from django.conf import settings

from shopify import ApiAccess, Session, session_token
from shopify.utils import shop_url

from .utils import get_shop_model


def shopify_embed(func):

    def wrapper(request, **kwargs):

        shop = request.GET.get('shop')
        response = func(request, **kwargs)
        if shop:
            ancestors = (
                f'frame-ancestors https://{shop} '
                'https://admin.shopify.com'
            )
            response['Content-Security-Policy'] = ancestors

        return response

    return wrapper


def shop_session(func):

    def wrapper(*args, **kwargs):
        try:

            request = args[0]

            authorization_header = request.META.get("HTTP_SHOPIFYAUTH")
            if (
                not authorization_header
                and request.user.is_authenticated
                and request.user.is_staff
            ):
                print('user is staff ')

            app_config = apps.get_app_config("shopify_app")
            decoded_session_token = session_token.decode_from_header(
                authorization_header=authorization_header,
                api_key=app_config.SHOPIFY_API_KEY,
                secret=app_config.SHOPIFY_API_SECRET,
            )

            shopify_domain = decoded_session_token.get("dest")
            shopify_domain = shopify_domain.removeprefix("https://")

            check_shop_domain(request, kwargs, shopify_domain)
            check_shop_known(request, kwargs)

            kwargs['shopify_user_id'] = decoded_session_token['sub']

            return func(*args, **kwargs)

        except session_token.SessionTokenError:
            return HttpResponse(status=401)

    return wrapper


def shopify_session(session_token):

    shopify_domain = session_token.get("dest").removeprefix("https://")
    api_version = apps.get_app_config("shopify_app").SHOPIFY_API_VERSION
    access_token = get_shop_model().objects.get(
        shopify_domain=shopify_domain
    ).shopify_token

    return Session.temp(shopify_domain, api_version, access_token)


def known_shop_required(func):
    def wrapper(*args, **kwargs):
        request = args[0]
        try:
            if settings.SHOPIFY_DEV_SHOPIFY_DOMAIN:
                shop_domain = settings.SHOPIFY_DEV_SHOPIFY_DOMAIN
            else:
                shop_domain = request.GET.get("shop", request.POST.get("shop"))

            check_shop_domain(request, kwargs, shop_domain)
            check_shop_known(request, kwargs)
        except Exception as e:
            print(e)
            raise ValueError("Shop must be known")
        finally:
            return func(*args, **kwargs)

    return wrapper


def check_shop_domain(request, kwargs, shop_domain):
    shop_domain = get_sanitized_shop_param(shop_domain)
    kwargs["shopify_domain"] = shop_domain
    request.shopify_domain = shop_domain
    return shop_domain


def get_sanitized_shop_param(shop_domain):
    sanitized_shop_domain = shop_url.sanitize_shop_domain(shop_domain)
    if not sanitized_shop_domain:
        raise ValueError("Shop must match 'example.myshopify.com'")
    return sanitized_shop_domain


def check_shop_known(request, kwargs):
    shop = get_shop_model().objects.get(
        shopify_domain=kwargs.get("shopify_domain")
    )
    kwargs["shop"] = shop
    request.shop = shop


def latest_access_scopes_required(func):
    def wrapper(*args, **kwargs):
        shop = kwargs.get("shop")

        try:
            configured_access_scopes = apps.get_app_config(
                "shopify_app"
            ).SHOPIFY_API_SCOPES
            current_access_scopes = shop.access_scopes

            assert ApiAccess(configured_access_scopes) == ApiAccess(
                current_access_scopes)
        except:
            kwargs["scope_changes_required"] = True

        return func(*args, **kwargs)

    return wrapper
