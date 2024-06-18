# django-telegram-bot

# How to run

## Quickstart: Polling & SQLite

The fastest way to run the bot is to run it in polling mode using SQLite database without all Celery workers for background jobs. This should be enough for quickstart:

``` bash
git clone https://github.com/ohld/django-telegram-bot
cd django-telegram-bot
```

Create virtual environment (optional)
``` bash
python3 -m venv dtb_venv
source dtb_venv/bin/activate
```

Install all requirements:
```
pip install -r requirements.txt
```

Create `.env` file in root directory and copy-paste this or just run `cp .env_example .env`,
don't forget to change telegram token:
``` bash 
DJANGO_DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
TELEGRAM_TOKEN=<PASTE YOUR TELEGRAM TOKEN HERE>
```

Run migrations to setup SQLite database:
``` bash
python manage.py migrate
```

Create superuser to get access to admin panel:
``` bash
python manage.py createsuperuser
```

Run bot in polling mode:
``` bash
python run_polling.py 
```

If you want to open Django admin panel which will be located on http://localhost:8000/tgadmin/:
``` bash
python manage.py runserver
```

## Run locally using docker-compose
If you want just to run all the things locally, you can use Docker-compose which will start all containers for you.

### Create .env file. 
You can switch to PostgreSQL just by uncommenting it's `DATABASE_URL` and commenting SQLite variable.
```bash
cp .env_example .env
```

### Docker-compose

To run all services (Django, Postgres, Redis, Celery) at once:
``` bash
docker-compose up -d --build
```

Check status of the containers.
``` bash
docker ps -a
```
It should look similar to this:
<p align="left">
    <img src="https://github.com/ohld/django-telegram-bot/raw/main/.github/imgs/containers_status.png">
</p>

Try visit <a href="http://0.0.0.0:8000/tgadmin">Django-admin panel</a>.

### Enter django shell:

``` bash
docker exec -it dtb_django bash
```

### Create superuser for Django admin panel

``` bash
python manage.py createsuperuser
```

### To see logs of the container:

``` bash
docker logs -f dtb_django
```

### Create Django super user
Being inside a container:
``` bash
python manage.py createsuperuser
```

After that you can open admin panel of your deployed app which is located at https://<YOURDOMAIN.COM>/tgadmin.

### Read app logs

``` bash
dokku logs dtb -t
```


----
