
# Fittin Тестовое Задание

Backend часть для интернет-магазина “Меха и шубы“ на Django


##  Обзор

Для авторизации/аутентификации используется библиотека [djangorestframework-simplejwt](https://github.com/jazzband/djangorestframework-simplejwt). Подключен автогенератор Swagger [drf-yasg](https://github.com/axnsan12/drf-yasg). Реализована сборка приложения через Docker. Добавлены unit-тесты для основных эндпоинтов. Интеграция с [Yandex ID](https://yandex.ru/dev/id/doc/ru/) для регистрации и авторизации<br/> ![email_image](https://github.com/git-gud-casual/fittin-test-task/blob/master/readme_imgs/password.png)

Рассылка email`ов через SMTP с автосгенерированным паролем при регистрации через Yandex ID, рассылка с информацией о добавленных скидках для пользователей, добавивших товар в избранное<br/> ![email_image](https://github.com/git-gud-casual/fittin-test-task/blob/master/readme_imgs/discount_info.png)

Настроено HTTPS соедниение через [nginx](https://nginx.org/ru/) с самоподписанным SSL сертификатом (публичный сертификат лежит в репозитории). PostgreSQL в качестве базы данных. Добавлена простая админка просто для просмотра. В проекте использовался [Github Actions](https://docs.github.com/ru/actions) для автодеплоя на домашний сервер.

Регистрация/авторизация через Yandex ID<br/>
https://46.72.238.25:8889/yandex/token/ 

Swagger<br/>
https://46.72.238.25:8889/swagger/

Админка<br/>
https://46.72.238.25:8889/admin/

Данные для авторизации

| Parameter | Value        | 
| :-------- | :----------- |
| Логин     | admin2       |
| Пароль    | H5*sQsnz5_i5 |

## Продукты и Категории
Реализованы вложенные категории и один эндпоинт для их получения. Добавлен fixture файл для автозаполнения базы данных категориями. 

Для товаров добавлены все основные эндпоинты перечисленные в ТЗ и один GET-эндпоинт для получения всех товаров. Цена хранится и передается в копейках. В эндпоинтах для получения списка товаров добавлены пагинация, сортировка по цене, фильтрация по цене. Сортировка и фильтрация по цене происходят с учетом скидки на товар. В ответе эндпоинтов приходят только те товары, которые доступны на складе.

Помимо основных моделей, добавлены модели скидки (ProductDiscount) и размера товара (ProductSize). 

При добавлении или обновлении информации о скидке происходит рассылка email`ов юзерам, добавивших товар в избранное. Рассылка происходит с помощью [Celery](https://docs.celeryq.dev/en/stable/) с [Redis](https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/redis.html) бекендом.

В ProductDiscount содержится информация о размере и количестве на складе, связан с Product свзяью один-к-одному.
## Корзина и Заказы

Для реализации функционала корзины добавлены модели Cart и CartEntry. Модель Cart связана один-к-одному с моделью django.contrib.auth.models.User (в проекте используется дефолтная Django модель для авторизации/аутентификации) и связью многие-к-многим с моделью ProductSize через дополнительную модель CartEntry, хранящую информацию о количестве товара в корзине. 

Для заказов реализованы модели Order и OrderEntry со связью многие-к-одному. Order хранит в себе дату заказа, флаг пометки оплаты заказа. OrderEntry содержит цену, количество товара и ссылку на товар. 

Реализованы основые эндпоинты из ТЗ. При создании заказа передаются размеры и idшники товаров, хранящихся в корзине. Проверяется имеются ли товары в нужном количестве на складе. Количество товаров на складе уменьшается на нужное число. Заказанные товары удаляются из корзины. При создании заказа атомарная транзакция.

Для использования этих эндпоинтов необходима авторизация.

## Интеграции
Реализована интеграция с [Yandex ID](https://yandex.ru/dev/id/doc/ru/how-to) для регистрации/авторизации. Добавлена рассылка сообщений через SMTP.

## Переменные среды

В example.env перечислены и подписаны необходимые переменные среды

![Deploy](https://github.com/git-gud-casual/fittin-test-task/actions/workflows/deploy-dev.yml/badge.svg?branch=master)
