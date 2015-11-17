# Jucy [![Build Status](https://travis-ci.org/Jucyio/Jucy.svg?branch=master)](https://travis-ci.org/Jucyio/Jucy)

Connect developers and customers through juicy feedback within GitHub.

#### Install the 1st time

```shell
# Install pre-requirements
# Debian, Ubuntu, and variants
apt-get install libpython-dev libffi-dev python-virtualenv libmysqlclient-dev nodejs
# Arch
pacman -S libffi python-virtualenv libmysqlclient nodejs

# Clone the repo
git clone git@github.com:Jucyio/Jucy.git
cd Jucy

# Create a virtualenv to isolate the package dependencies locally
virtualenv env
source env/bin/activate

# Install packages, no need to be root
pip install -r requirements.txt

# Create tables, initialize database
python manage.py migrate

# Compile localized messages
python manage.py compilemessages

# Download front-end dependencies
npm install -g bower less
bower install

# Compile LESS to CSS
lessc -x web/static/less/style.less web/static/css/style.css
```

#### Anytime

##### Reactivate the environment
```shell
source env/bin/activate
```

##### Launch the server

```shell
python manage.py runserver
```
If you want it to be externally visible, add an extra argument `0.0.0.0:8000`.

No need to restart it to see your modifications, the server reloads itself automatically.

##### Whenever you change the models

```shell
python manage.py makemigrations
python manage.py migrate
```

##### Whenever you add messages that should be translated

Generate terms:
```shell
python manage.py makemessages -l ja --ignore=env/*
```

Then go to [POEditor](https://poeditor.com/projects/view?id=29518) and import the tems. When the new terms are translated in all languages, generate the new files and put them in the repo. Either manually or using the [POEditor integration](https://poeditor.com/github/projects).

Compile all languages
```shell
python manage.py compilemessages
```

#### Configure

To use your own configuration values, create a file `jucy/local_settings.py` and never commit it to the repo.

You may need to override those values:

###### In a production environment

```python
# Production Basics
SECRET_KEY = 'random generated string to change in production'
DEBUG = False
TEMPLATE_DEBUG = False
ALLOWED_HOSTS = ['jucy.io']

DATABASES = {
    'default': {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': 'jucy',
    'OPTIONS': {'charset': 'utf8mb4'},
    'USER': 'root',
    'PASSWORD': '',
    'HOST': 'localhost',
    'PORT': '3306',
  }
}
```

###### In a testing environment

```python
# To log all the 500 errors in the terminal:
LOGGING = {
    'disable_existing_loggers': False,
    'version': 1,
    'handlers': {
    'console': {
      'class': 'logging.StreamHandler',
      'level': 'DEBUG',
    },
  },
    'loggers': {
      'django.request': {
      'handlers': ['console'],
      'level': 'DEBUG',
      'propagate': True,
  },
},
}
```
