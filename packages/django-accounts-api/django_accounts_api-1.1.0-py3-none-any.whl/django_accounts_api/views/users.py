import re
from typing import Any, Dict

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core import serializers
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic.edit import UpdateView, DeleteView
from django.views.generic.list import BaseListView


User = get_user_model()

# Setting to control the fields returned by the user api
USER_FIELD_SETTTING = 'ACCOUNTS_API_USER_FIELDS'
# DEfault fields returned byt he user aPI if no setting provided
DEFAULT_USER_FIELDS = [
    'username',
    'first_name',
    'last_name',
    'email',
    'last_login',
    'is_active',
]

def _is_user_perm(perm_codename: str):
    ''' returns true if the permission codename relates to the configured user model'''
    match =  re.match(
        f'^{User._meta.app_label}\.[\w]+_{User._meta.model_name}',
        perm_codename
    )
    return match

def _user_has_any_user_perm(user):
    ''' returns true if the user has any permission related to the configured user model'''
    perms = user.get_all_permissions()
    return any(
        filter(
            lambda perm: _is_user_perm(perm),
            perms
        )
    )

def _user_has_user_perm(user: AbstractUser, perm: str):
    ''' returns true if the user has the specified permission on the configured user model'''
    return user.has_perm(f'{User._meta.app_label}.{perm}_{User._meta.model_name}')

class JsonListView(BaseListView):
    ''' Extends the django base list view to return json serialized data
    '''
    def render_to_response(self, context, **response_kwargs):
        queryset = self.get_queryset()
        response = HttpResponse(
           serializers.serialize("json", queryset, fields=self.get_fields())
        )
        response.headers['Content-Type'] = 'application/json'
        return response

@method_decorator(never_cache, name='dispatch')
class APIUsersView(JsonListView):
    ''' Returns a json serialized list of user models
    
    
    '''
    model = User
    fields_setting_name = None

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        if not _user_has_any_user_perm(request.user):
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)

    
    def get_fields(self):
        return getattr(settings, USER_FIELD_SETTTING, DEFAULT_USER_FIELDS)

class UserUpdate(UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email', 'is_active']
    template_name = 'django_accounts_api/schemas/user_update.json'
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        if not _user_has_user_perm(request.user, 'change'):
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        response = JsonResponse(form.errors)
        response.status_code = 400
        return response

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.save()
        return HttpResponse(status=200)

    def render_to_response(self, context: Dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        response = super().render_to_response(context, **response_kwargs)
        response['Content-Type'] = 'application/json'
        return response


class UserDelete(DeleteView):
    model = User
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        if not _user_has_user_perm(request.user, 'delete'):
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.object.delete()
        return HttpResponse(status=200)

    def render_to_response(self, context: Dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        return HttpResponse(status=200)




