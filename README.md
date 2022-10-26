![yamdb_workflow]
(https://github.com/distemper17/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

### Описание проекта:

Проект разработан как инструмент сбора данных о произведениях.

Проект YaMDb собирает отзывы (Review) пользователей на произведения (Titles). Произведения делятся на категории: "Книги", "Фильмы", "Музыка". Список категорий (Category) может быть расширен 
администратором.

Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.
В каждой категории есть произведения: книги, фильмы или музыка. Например, в категории "Книги" могут быть произведения "Винни-Пух и все-все-все" и "Марсианские хроники", а в категории "Музыка" — песня "Давеча" группы "Насекомые" и вторая сюита Баха.

Произведению может быть присвоен жанр (Genre) из списка предустановленных (например, "Сказка", "Рок" или "Артхаус"). Новые жанры может создавать только администратор.

Благодарные или возмущённые пользователи оставляют к произведениям текстовые отзывы (Review) и ставят произведению оценку в диапазоне от одного до десяти; из пользовательских оценок формируется усреднённая оценка произведения — рейтинг. На одно произведение пользователь может оставить только один отзыв.

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/yandex-praktikum/api_yamdb.git
```

```
cd api_yamdb
```

Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

```
. venv/Scripts/activate
```

```
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
cd api_yamdb/
```

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```

### Дальнейшее использование:

Загрузите приложение для осуществления запросов к api (например Postman).

В приложении укажите расположение сервера (стандартно: http://127.0.0.1:8000/) + необходимую команду.

Для неаутентифицированных пользователей многие запросы недоступны. Аноним может просматривать описания произведений, читать отзывы и комментарии.

Для получения доступа к иным функциям, необходимо зарегистрироваться и получить токен:
1. Пользователь отправляет POST-запрос с параметрами email и username на эндпоинт /api/v1/auth/signup/.
2. Сервис YaMDB отправляет письмо с кодом подтверждения (confirmation_code) на указанный адрес email.
3. Пользователь отправляет POST-запрос с параметрами username и confirmation_code на эндпоинт /api/v1/auth/token/, в ответе на запрос ему приходит token (JWT-токен).

В результате пользователь получает токен и может работать с API проекта, отправляя этот токен с каждым запросом.
После регистрации и получения токена пользователь может отправить PATCH-запрос на эндпоинт /api/v1/users/me/ и заполнить поля в своём профайле.

### Пример запросов:

## Получение произведения по id:

Пользователь отправляет GET запрос на адрес /api/v1/titles/{номер id} для получения информации о произведении.

## Проставление оценки произведению:

Пользователь отправляет POST запрос на адрес /api/v1/titles/{номер id}/reviews с указанием оценки, которую пользователь желает присвоить произведению (от 1 до 10). Пользовательская оценка будет сохранена в базе данных.

### Технологии в работе:

Для работы в данном проекте используются следующие технологии:
```
python (версия 3.7.0)
```
```
django (версия 2.2.16)
```

Модули для джанги, включая:
```
PyJWT, simplejwt (для работы с токенами)
```
```
RestFramework (для работы с API)
```
```
django-filter (для дополнительных возможностей фильтрации)
```
```
pytest (для целей тестирования и TDD)
```

### Наполнение .env-файла
```
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
```
```
DB_NAME=postgres # имя базы данных
```
```
POSTGRES_USER=postgres # логин для подключения к базе данных
```
```
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
```
```
DB_HOST=db # название сервиса (контейнера)
```
```
DB_PORT=5432 # порт для подключения к БД 
```

### Команды для запуска приложения в контейнере

В первую очередь, необходимо сделать образ. Для этого переходим в директорию Докерфайла и запускаем образ:
```
docker build -t <название образа> .
```
Далее, создаем контейнеры Docker Compose:
```
docker-compose up
```
Производим миграции и добавляем статику:
```
docker-compose exec web python manage.py migrate
```
```
docker-compose exec web python manage.py createsuperuser
```
```
docker-compose exec web python manage.py collectstatic --no-input 
```

### Команды для заполнения базы данными

После запуска контейнера, делаем запросы через Postman или другой api сервис (как указано выше) на создание записей в БД. Для наполнения локального проекта данными, выполняем:
```
docker-compose exec web python manage.py dumpdata > fixtures.json
```

Автор - начинающий программист, который немного опаздал с дедлайном по этому спринту:
telegram - @alexlonskiy
github - @distemper17

License:
MIT License
Copyright (c) 2022 distemper17