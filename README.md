### Info
url: https://tabularasa.hopto.org/

email: superuser@example.com

username: useradmin

password: Change_me!


# Фудграм
Проект "Фудграм" - это готовый сайт, где можно делиться своими любимыми рецептами и находить новые интересные блюда. 
На этом сайте аутентифицированные пользователи могут:

   * публиковать свои собственные рецепты;
   * просматривать и добавлять в избранное рецепты других авторов;
   * подписываться на других авторов, чтобы получать уведомления о новых рецептах;

На сайте реализован удобный сервис "Список покупок", который составляет общий список продуктов, необходимых для приготовления выбранных блюд.

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/iurelen/foodgram-project-react.git
```

```
cd backend
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

* Если у вас Linux/macOS

    ```
    source env/bin/activate
    ```

* Если у вас windows

    ```
    source env/scripts/activate
    ```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```
