from django.conf import settings
from django.contrib.auth.models import User as DjangoUser
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import reverse
from django.utils.module_loading import import_string
from django.views.generic import View

def user_details(user: DjangoUser) -> dict:
    """The details of the user to return on success"""
    extra = {}
    add_extra_path = getattr(settings, "ACCOUNT_API_DETAILS", False)
    if add_extra_path:
        try:
            details_func = import_string(add_extra_path)
            extra = details_func(user)
        except ImportError:
            pass

    return dict(
        id=user.pk,
        name=user.get_full_name(),
        **extra
    )


class AcceptJsonMixin:
    """
    Adds method to detect if JSON was requested in the Accept header
    """

    def json_response_requested(self: View) -> bool:
        """ does the request want JSON content back?"""
        if "HTTP_ACCEPT" in self.request.META:
            return self.request.META["HTTP_ACCEPT"] == "application/json"
        return False


def manifest(request: HttpRequest) -> HttpResponse:
    """Return a json encoded dictionary {name: path} for views offered
    by Django Accounts API

    :param request: the Django http request
    :type request: HttpRequest
    :return: json encoded name: path dictionary
    :rtype: HttpResponse
    """
    return JsonResponse(dict(
        login=reverse("django_accounts_api:login"),
        logout=reverse("django_accounts_api:logout"),
        password_change=reverse("django_accounts_api:password_change"),
        password_reset=reverse("django_accounts_api:password_reset"),
        password_reset_confirm=reverse(
            "django_accounts_api:password_reset_confirm",
            kwargs=dict(uidb64="uidb64", token="token")
        ),

        users=reverse("django_accounts_api:users"),
        user_create=reverse("django_accounts_api:user_create"),
        user_update=reverse(
            "django_accounts_api:user_update",
            kwargs=dict(pk=00000)
        ),
        user_delete=reverse(
            "django_accounts_api:user_delete",
            kwargs=dict(pk=00000)
        ),
        user_reset=reverse(
            "django_accounts_api:user_reset",
            kwargs=dict(pk=00000)
        )
    ))
