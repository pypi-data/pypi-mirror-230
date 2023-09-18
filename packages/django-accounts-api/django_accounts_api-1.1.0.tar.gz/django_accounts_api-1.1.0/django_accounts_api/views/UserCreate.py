from typing import Any

from django_accounts_api.forms.user_create import UnusablePasswordUserCreationForm
from django_accounts_api.views.users import _user_has_user_perm

from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, JsonResponse
from django.views.generic.edit import FormView

from .base import AcceptJsonMixin
from .UserReset import ResetPasswordMixin

class UserCreate(AcceptJsonMixin, ResetPasswordMixin, FormView):
    """ Create a user from the basic name and email information
    Do not set the password, but generate a link to set it
    """
    form_class = UnusablePasswordUserCreationForm
    template_name = 'django_accounts_api/form.html'

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        if not _user_has_user_perm(request.user, 'add'):
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)

    def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        if self.json_response_requested():
            return JsonResponse(
                [
                    {
                        'type': 'text'
                    }
                ],
                safe=False
            )
        else:
            return super().render_to_response(context, **response_kwargs)

    def form_invalid(self, form: Any) -> HttpResponse:
        if self.json_response_requested():
            response = JsonResponse(
                form.errors
            )
            response.status_code = 400
        else:
            response = super().form_invalid(form)
            response.status_code = 400
        return response

    
    def form_valid(self, form: Any) -> HttpResponse:
        self.user = form.save()
        self.set_reset_link(self.user)
        return HttpResponse(self.reset_link, status=200)