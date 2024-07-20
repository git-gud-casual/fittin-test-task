from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class UsernameOrEmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user_clazz = get_user_model()
        print(username)
        try:
            user = user_clazz.objects.get(Q(email__iexact=username) | Q(username=username))
            if user.check_password(password):
                return user
        except user_clazz.DoesNotExist:
            pass
        return None
