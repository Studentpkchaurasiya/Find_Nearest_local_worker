from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from rest_framework_simplejwt.tokens import AccessToken
from .models import User
from jwt import ExpiredSignatureError

class JWTFromCookieAuthentication(BaseAuthentication):
    def authenticate(self , request):
        token = request.COOKIES.get('access_token')
        if not token:
            return None
        try:
            validate_token = AccessToken(token)
            user_id = validate_token['user_id']
            user = User.objects.get(id=user_id)
            return (user,None)
        except ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token expired')
        except Exception as e:
            raise exceptions.AuthenticationFailed('Invalid token')
            