# django-redis-data-manager

A simple django application provide simple redis cache data manager functional.


## Install

```
pip install django-redis-data-manager
```

- If you want to use guniocrn web server, install `gunicorn` it by yourself.
- If you want to use mysql database, install `mysqlclient` by yourself.

## Install Server Command

- manage-django-redis-data-manager

**Command Help**

```
C:\Workspace\redis-dataman>manage-django-redis-data-manager

Type 'manage-django-redis-data-manager help <subcommand>' for help on a specific subcommand.

Available subcommands:

[auth]
    changepassword
    createsuperuser

[contenttypes]
    remove_stale_contenttypes

[django]
    check
    compilemessages
    createcachetable
    dbshell
    diffsettings
    dumpdata
    flush
    inspectdb
    loaddata
    makemessages
    makemigrations
    migrate
    sendtestemail
    shell
    showmigrations
    sqlflush
    sqlmigrate
    sqlsequencereset
    squashmigrations
    startapp
    startproject
    test
    testserver

[django_server_controller]
    wsgi-server

[sessions]
    clearsessions

[staticfiles]
    collectstatic
    findstatic
    runserver
```

## Usage

- We will try to load your private settings from `django_redis_data_manager_project_local_settings.py` module.
- By default the admin site registered under path: `/admin/`. You can change it by set `ADMIN_SITE_URL=<your site path>` in `django_redis_data_manager_project_local_settings.py`.
- By default we try to use sqlite3 database. You can change it by set new `DATABASES` in `django_redis_data_manager_project_local_settings.py`.

## Releases

### v0.1.0

- First release.

### v0.1.1

- Add depends package in requirements.txt.

### v0.1.2

- Add `ADMIN_SITE_URL` to custom admin site register url.
- Add default WSGI_SERVER_ENGINE to `gunicorn`, and add the default `uwsg.conf.py` which will let the server listen on `16379` port to do service.

### v0.1.3

- Fix static link problem.

### v0.1.4

- Add django_safe_fields in app_requires.
- Setup fix.

### v0.1.5

- Show json in pretty way.

### v0.1.6

- Fix dependence package version problem.

### v0.1.7

- Doc update.
