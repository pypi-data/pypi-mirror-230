from http import HTTPStatus
from typing import Any
import warnings

from django.contrib.auth.models import User as DjangoUser
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.debug import sensitive_post_parameters

from .base import AcceptJsonMixin, user_details


@never_cache
def login_check(request) -> HttpResponse:
    """
    200 and details if logged in, 401 if not

    User details are basic, but can be expanded by providing a dotted import path to a 
    function returning a json serializable dict from the user parameter
    """
    warnings.warn("This endpoint is deprecated", DeprecationWarning)
    user: DjangoUser = request.user
    if (user.is_authenticated):
        return JsonResponse(user_details(user))
    else:
        return HttpResponse(status=401)


@method_decorator(ensure_csrf_cookie, name='get')
@method_decorator(sensitive_post_parameters(), name='dispatch')
class Login(AcceptJsonMixin, LoginView):
    '''
    Override the Django login view to be API friendly for json or partial html

    GET:

    - default: renders a partial login form
    - json requested: json form schema

    POST success: 200 logs the user in
     
    POST failure: 400

    - default: renders a password form with errors
    - json requested: returns password form errors

    '''
    template_name = "django_accounts_api/login.html"

    def form_valid(self, form):
        """Override redirect behavior to return JSON user details"""
        _repressed_redirect = super().form_valid(form)  # noqa: F841
        return JsonResponse(
            user_details(self.request.user),
            status=201
        )

    def form_invalid(self, form):
        """Override redirect behavior if json is requested return json errors"""
        if self.json_response_requested():
            return JsonResponse(dict(errors=form.errors), status=400)
        else:
            return super().form_invalid(form)

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        """Override the get behavior if json requested return user details"""
        if self.json_response_requested():
            if (request.user.is_authenticated):
                return JsonResponse(user_details(request.user))
            else:
                return JsonResponse({}, status=HTTPStatus.NO_CONTENT)
        else:
            return super().get(request, *args, **kwargs)


class Logout(LogoutView):
    ''' Override the Django logout view to NOT redirect on successful login
    
    POST - logs out, returns 200
    '''

    def post(self, request, *args, **kwargs):
        _repressed_redirect_or_render = super().post(request, *args, **kwargs)  # noqa: F841
        return HttpResponse(
            status=200
        )
