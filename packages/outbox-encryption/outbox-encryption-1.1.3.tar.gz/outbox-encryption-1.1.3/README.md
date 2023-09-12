# DJANGO OUTBOX ENCRYPTION

Sometimes, when you ready to publish your project to server. 

There is a slight change between the application settings on the local and the server.
Such as database name, password, etc.
The second thing, is you need to encrypt information like password or other.
The last one, you need to automatically select setting local when you work on local computer, and auto select server when application running on server.

You are on the right path...


## Install package to your environment
    > pip install outbox-encryption

## How it works
    On developing time, library will scan your environment variable
    to get file name specific for you computer, for example : .env-outbox-python
    this file must exists on your source code to make application continue.

    On deploy time, for example your local computer, library again will scan your
    environment variable and get file name base on computer where it running

    if file found, application continue, else stop application

    if you ready to deploy to server, just rename file .env-outbox-python to name 
    which is must be found on server

## How to use 

### Create Encrypt File    
    > python manage.py shell

    > from encryption import OutboxEncryption
    > lib = OutboxEncryption()
    > mplaint_text = {
            'DB_PASSWORD': '',
            'SECRET_KEY': 'xxg_7me8rl2m#a_h2oresgt2#ni=3_4*!ai*=rtsq)yi!g7_5-51xx'
        }
    > lib.enc_environ(mplaint_text)
    # new file is created (maybe file is hidden, CTRL+H to show it)

    # Open new file that recently created
        You have to write other setting that no encrypt apply, such as:

        DEBUG=True
        UNDER_CONSTRUCTION=False
        DB_ENGINE=django.db.backends.mysql
        DB_NAME=db_name
        DB_USER=root
        DB_HOST=127.0.0.1
        DB_PORT=3306

#### Note:
    File name auto create base on environment variable on running computer.
    If run on server just rename this file, and write setting needed to run website on server

### Decrypt environment file
    > python manage.py shell

    > from encryption import OutboxEncryption
    > lib = OutboxEncryption()

    > mplaint_key = {
        'DB_PASSWORD',
        'SECRET_KEY'
        }
    > mplaint_list = {
        'ALLOWED_HOSTS',
        'CSRF_TRUSTED_ORIGINS'
        }
    > key = lib.dec_environ(mplaint_key, mplaint_list)
    > print (key)

### Change your settings.py file
    # Write inside settings.py (django project settings): 

    > from encryption import OutboxEncryption
    > lib = OutboxEncryption()

    # List of key variable that must be encrypt or decrypt before set or get data
    > mplaint_key = ['DB_PASSWORD', 'SECRET_KEY']

    Variable that must be cast as list from environmnet to settings.py
    > mplaint_list = ['ALLOWED_HOSTS', 'CSRF_TRUSTED_ORIGINS']

    Variable that must be cast as tuple from environment to settings.py
    > mplaint_tuple = ['SECURE_PROXY_SSL_HEADER']

    Get encryption data
    > key = lib.decrypt_environ(mplaint_key, mplaint_list, mplaint_tuple)

    Setting variable :
    > DEBUG = key['DEBUG']
    > UNDER_CONSTRUCTION = key['UNDER_CONSTRUCTION']
    > DEBUG = key['DEBUG']
    > SECRET_KEY = key['SECRET_KEY']
    > ALLOWED_HOSTS = key['ALLOWED_HOSTS']

    > tmp_engine = key['DB_ENGINE']
    > if 'sqlite3' in tmp_engine:
        DATABASES = {
            'default': {
                'ENGINE': tmp_engine,                
                'NAME': key['DB_NAME'],   # complete path 
            }
        }
    > else: # default 
    >   DATABASES = {
            'default': {
                'ENGINE'    : key['DB_ENGINE'],
                'NAME'      : key['DB_NAME'],
                'USER'      : key['DB_USER'],
                'PASSWORD'  : key['DB_PASSWORD'],
                'HOST'      : key['DB_HOST'],
                'PORT'      : key['DB_PORT'],
            }

    > SECURE_PROXY_SSL_HEADER = key['SECURE_PROXY_SSL_HEADER']

    # Optional:
    > tmp = key.get('CSRF_TRUSTED_ORIGINS') 
    > if tmp:
    >   CSRF_TRUSTED_ORIGINS=key['CSRF_TRUSTED_ORIGINS']

    # # use default value if setting not exists
    > tmp = key.get('STATIC_ROOT')  # True if exists, None if not exists
    > STATIC_ROOT = key['STATIC_ROOT'] if tmp else os.path.join(BASE_DIR, 'staticfiles')

    > tmp = key.get('MEDIA_ROOT')
    > MEDIA_ROOT = key['MEDIA_ROOT'] if tmp else os.path.join(BASE_DIR, 'media')


    
    
