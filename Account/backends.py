from django.contrib.auth.backends import ModelBackend
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from .models import User

class UserAuthenticationBackend(ModelBackend):

    def authenticate(self, **kwargs):
        user = None
        if 'registered_by' in kwargs and kwargs["registered_by"] == "manual":
            if 'password' in kwargs and kwargs["password"] != "":
                email = kwargs["email"]
                password = kwargs["password"]
                registered_by = kwargs["registered_by"]

                try:
                    user = User.objects.get(email=email, password=password, registered_by=registered_by)
                except User.DoesNotExist:
                    user = None
            else:
                return AuthenticationFailed(code=status.HTTP_400_BAD_REQUEST, default_detail = ('Password cannot be blank.'), default_code = 'user_credentials_not_valid')
        elif (('registered_by' in kwargs and kwargs["registered_by"] =="google") or ('registered_by' in kwargs and kwargs["registered_by"] =="facebook") or ('registered_by' in kwargs and kwargs["registered_by"] =="apple")):
            if 'social_id' in kwargs and kwargs["social_id"] != "":
                email = kwargs["email"]
                social_id = kwargs["social_id"]
                registered_by = kwargs["registered_by"]

                try:
                    user = User.objects.get(email=email, social_id=social_id, registered_by=registered_by)
                except User.DoesNotExist:
                    user = None
            else:
                return AuthenticationFailed(code=status.HTTP_400_BAD_REQUEST, default_detail = ('social_id cannot be blank.'), default_code = 'user_credentials_not_valid')
        else:
            email = kwargs["username"]
            password = kwargs["password"]

            try:
                user = User.objects.get(email=email, password=password)
            except User.DoesNotExist:
                user = None
        return user