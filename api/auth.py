from django.contrib.auth import get_user_model
from ninja.errors import HttpError
from ninja.security import HttpBearer
from ninja_jwt.exceptions import TokenError
from ninja_jwt.tokens import AccessToken

User = get_user_model()


class JWTAuth(HttpBearer):
    def authenticate(self, request, token: str):
        try:
            validated_token = AccessToken(token)
            return User.objects.get(id=validated_token["user_id"], is_active=True)

        except TokenError as e:
            raise HttpError(401, str(e))

        except User.DoesNotExist:
            raise HttpError(401, "User associated with the token does not exist.")
