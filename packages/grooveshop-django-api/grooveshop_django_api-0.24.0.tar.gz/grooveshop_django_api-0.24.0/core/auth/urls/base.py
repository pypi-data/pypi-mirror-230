from dj_rest_auth.app_settings import api_settings
from django.urls import path

from core.auth.views.base import AuthLoginView
from core.auth.views.base import AuthLogoutView
from core.auth.views.base import AuthPasswordChangeView
from core.auth.views.base import AuthPasswordResetConfirmView
from core.auth.views.base import AuthPasswordResetView
from core.auth.views.base import AuthUserDetailsView

urlpatterns = [
    # URLs that do not require a session or valid token
    path(
        "password/reset/", AuthPasswordResetView.as_view(), name="rest_password_reset"
    ),
    path(
        "password/reset/confirm/",
        AuthPasswordResetConfirmView.as_view(),
        name="rest_password_reset_confirm",
    ),
    path("login/", AuthLoginView.as_view(), name="rest_login"),
    # URLs that require a user to be logged in with a valid session / token.
    path("logout/", AuthLogoutView.as_view(), name="rest_logout"),
    path("user/", AuthUserDetailsView.as_view(), name="rest_user_details"),
    path(
        "password/change/",
        AuthPasswordChangeView.as_view(),
        name="rest_password_change",
    ),
]

if api_settings.USE_JWT:
    from rest_framework_simplejwt.views import TokenVerifyView

    from dj_rest_auth.jwt_auth import get_refresh_view

    urlpatterns += [
        path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
        path("token/refresh/", get_refresh_view().as_view(), name="token_refresh"),
    ]
