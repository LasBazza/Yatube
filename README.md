# Yatube
***Yatube*** - это блог, в котором пользователи могут делиться записями и публиковать фото. 

Реализована система атунтификации пользователей - каждый желающий может зарегестрироваться на сайте. Доступно восстановление пароля по электронной почте.

Есть возможность подписываться на других пользователей, создавать группы и публиковать записи в них, а также оставлять комментарии к записям.


Разработан на основе фреймворка Django 2.2, использованы разметка и стили Bootstrap.

* Python 3.8
* Django 2.2
* Bootstrap
* Gunicorn
* PostgreSQL
* Docker
* Nginx

## Запуск проекта

**1. Склонировать репозиторий**

```
git clone https://github.com/LasBazza/Yatube.git
```

**2. Заполнить файл _.env_ и поместить его в корневую папку проекта**

```
DEBUG=False
SECRET_KEY=django_secret_key
ALLOWED_HOSTS=web

DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
DB_HOST=db
DB_PORT=5432
```

**3. Запустить docker-compose**

Выполнить в корневой папке проекта команду

```
docker-compose up
```


**4. Создать суперпользователя**

```
docker-compose exec web python manage.py createsuperuser
```

Проект доступен на http://127.0.0.1/. Админ-панель django на http://127.0.0.1/admin/.
