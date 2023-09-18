import re

from django.conf import settings
from django.contrib import auth, messages
from django.shortcuts import redirect
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache

from authlib.google import GoogleOAuth2Client
from authlib.views import retrieve_next, set_next_cookie


ADMIN_OAUTH_PATTERNS = settings.ADMIN_OAUTH_PATTERNS
ADMIN_OAUTH_LOGIN_HINT = "admin-oauth-login-hint"
ADMIN_OAUTH_CREATE_USER_CALLBACK = getattr(
    settings,
    "ADMIN_OAUTH_CREATE_USER_CALLBACK",
    None,
)


@never_cache
@set_next_cookie
def admin_oauth(request):
    client = GoogleOAuth2Client(
        request, login_hint=request.COOKIES.get(ADMIN_OAUTH_LOGIN_HINT) or ""
    )

    if all(key not in request.GET for key in ("code", "oauth_token")):
        return redirect(client.get_authentication_url())

    try:
        user_data = client.get_user_data()
    except Exception as exc:
        messages.error(request, exc)
        messages.error(request, _("Error while fetching user data. Please try again."))
        return redirect("admin:login")

    email = user_data.get("email")
    if email:
        for pattern, user_mail in ADMIN_OAUTH_PATTERNS:
            match = re.search(pattern, email)
            if match:
                if callable(user_mail):
                    user_mail = user_mail(match)  # noqa: PLW2901
                user = auth.authenticate(email=user_mail)
                if not user and ADMIN_OAUTH_CREATE_USER_CALLBACK:
                    fn = import_string(ADMIN_OAUTH_CREATE_USER_CALLBACK)
                    fn(request, user_mail)
                    user = auth.authenticate(email=user_mail)
                if user and user.is_staff:
                    auth.login(request, user)
                    response = redirect(retrieve_next(request) or "admin:index")
                    response.set_cookie(
                        ADMIN_OAUTH_LOGIN_HINT, email, expires=30 * 86400
                    )
                    return response

        messages.error(
            request, _("No matching staff users for email address '%s'") % email
        )
    else:
        messages.error(request, _("Could not determine your email address."))
    response = redirect("admin:login")
    response.delete_cookie(ADMIN_OAUTH_LOGIN_HINT)
    return response


def create_superuser(request, email):
    user_model = auth.get_user_model()
    if user_model.objects.filter(email=email).exists() is False:
        user = user_model(email=email, is_active=True, is_staff=True, is_superuser=True)
        if user.USERNAME_FIELD != "email":
            setattr(user, user.USERNAME_FIELD, email)
        user.save()
