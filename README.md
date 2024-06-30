# Проект

![python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green)

![PostgreSQL](https://img.shields.io/badge/postgresql-4169e1?style=for-the-badge&logo=postgresql&logoColor=white)
![JSON Web Tokens](https://img.shields.io/badge/JWT-000?logo=jsonwebtokens&logoColor=fff&style=for-the-badge)

![JSON](https://img.shields.io/badge/JSON-000?logo=json&logoColor=fff&style=for-the-badge)
![YAML](https://img.shields.io/badge/YAML-CB171E?logo=yaml&logoColor=fff&style=for-the-badge)

![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?logo=gunicorn&logoColor=fff&style=for-the-badge)

![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=000&style=for-the-badge)

![Postman](https://img.shields.io/badge/Postman-FF6C37?logo=postman&logoColor=fff&style=for-the-badge)

Это готовый сайт, где можно делиться своими любимыми рецептами и находить новые интересные блюда. 
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
