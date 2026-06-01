from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth.models import AnonymousUser
from .models import User

class AccessTokenRotationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        access_token = request.COOKIES.get("access_token")
        refresh_token = request.COOKIES.get("refresh_token")

        request.user = AnonymousUser()  # default → not logged in

        if access_token:

            try:
                #  Validate current access token
                token = AccessToken(access_token)
                user_id = token["user_id"]
                request.user = User.objects.get(id=user_id)
                AccessToken(access_token)
                return  # Still valid
            except TokenError:
                #  Access token expired → try refresh
                if refresh_token:
                    try:
                        refresh = RefreshToken(refresh_token)
                        refresh.check_exp()  # ensures refresh expiration checked
                        new_access = refresh.access_token
                        request.new_access_token = str(new_access)
                        user_id = refresh["user_id"]
                        request.user = User.objects.get(id=user_id)
                        return
                    except TokenError:
                        #  Refresh token also invalid/expired → force logout immediately
                        request.force_logout = True

        elif refresh_token:
            # No access token, but refresh available → try to issue new access token
            try:
                refresh = RefreshToken(refresh_token)
                refresh.check_exp()  #  validate expiry
                new_access = refresh.access_token
                request.new_access_token = str(new_access)
                user_id = refresh["user_id"]
                request.user = User.objects.get(id=user_id)
            except TokenError:
                #  Refresh expired → logout
                request.force_logout = True

    def process_response(self, request, response):
        if getattr(request, "new_access_token", None):
            #  Replace access token in cookies
            response.set_cookie(
                key="access_token",
                value=request.new_access_token,
                httponly=True,
                samesite="Lax",
                secure=False,
            )

        if getattr(request, "force_logout", False):
            #  Immediately clear cookies
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")

        return response
