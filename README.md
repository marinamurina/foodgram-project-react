# praktikum_new_diplom

## Установка
* склонируйте репозиторий 
* в папке проекта создайте и активируйте виртуальное окружение:
    * cd api_yamdb
    * python3 -m venv venv
    * source venv/bin/activate (Linux, MacOS), venv/Scripts/acrivate (Win)
* установите необходимые пакеты:
    * pip install -r requirements.txt
* проведите миграции:
    * cd api_yamdb
    * python manage.py makemigrations
    * python manage.py migrate
* запустите сервер разработчика:
    * python manage.py runserver

Теперь можно выполнять запросы к эндпоинтам

## Загрузка базы данных из файлов csv
Осуществляется при помощи management command "PY manage.py <имя файла команды>", например - 
"PY manage.py import_ingredients".

## Описание API и запросов

Примеры запросов можно получить по адресу http://127.0.0.1:8000/redoc/ после запуска проекта

## Автор
    Марина Мурина https://github.com/marinamurina