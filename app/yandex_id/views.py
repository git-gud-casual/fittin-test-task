from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken

import requests

from django.conf import settings


def get_token_page(request: HttpRequest) -> HttpResponse:
    message = "<a href=\"https://oauth.yandex.ru/authorize?" + \
              "response_type=code&client_id=4fa9cb22324047cba05d3ffeab4deeb7\">Авторизоваться через Yandex ID</a>"
    if code := request.GET.get("code"):
        message = "Ошибка при запросе OAuth токена Yandex.ID"
        if (resp := requests.post("https://oauth.yandex.ru/token",
                                  data={"grant_type": "authorization_code",
                                        "code": code,
                                        "client_secret": settings.YDX_CLIENT_SECRET,
                                        "client_id": settings.YDX_CLIENT_ID})).ok:
            access_token = resp.json()["access_token"]
            data = requests.get("https://login.yandex.ru/info",
                                headers={"Authorization": f"OAuth {access_token}"}).json()
            try:
                user = User.objects.get_by_natural_key(data["login"])
            except User.DoesNotExist:
                password = User.objects.make_random_password()
                user = User.objects.create_user(
                    data["login"], data["default_email"], password,
                    first_name=data["first_name"], last_name=data["last_name"]
                )
                send_mail(
                    "Пароль",
                    f"Логин: {data['default_email']}\n"
                    f"Пароль: {password}", None,
                    [data["default_email"]], fail_silently=True
                )
            refresh = RefreshToken.for_user(user)
            return JsonResponse({"refresh": str(refresh), "access": str(refresh.access_token)})
    return render(request, "error.html", {"message": message})
