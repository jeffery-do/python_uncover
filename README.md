# Python Uncover
This is a dockerized flask applications that let's users do the following.

- Enter their preferences for certain artists
- Get recommendations of artists they may like. (Using a collaberative filtering algorithm)

### Tech Stack
- nginx
- postgres
- flask
- docker
- turicreate

``NOTE: the env_file is not included in this repo. Follow the format in setup instructions to make your own.``

### Setup Instructions
You must first install docker. Installing the latest docker should suffice.

After that, you must run a `docker build -t pythonuncover_flaskapp .` to build the application docker image

You must place an env_file in the root directory following this format.
```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=userPass
POSTGRES_DB=postgres
DB_USER=postgres
DB_PASS=userPass
DB_NAME=postgres
PG_TRUST_LOCALNET=true
APP_SECRET_KEY=supersecretkeyofsupersecretness
GRAPHLAB_KEY=<YOUR TURI GRAPHLAB KEY>
```
If you do not have a graphlab key, you must create one from their website.

To get this app to run, you must first initalize the database.
Start off by navigating to this repo's root folder.
### To initalize the database:
```
docker-compose up -d db # spin up your database in a detached way

# you will need to populate your postgres database...

# This must be done within the python_unconver image as it needs to be within the same network.
docker ps # see what the running container id is.
docker exec <container-id> -it bash

# then do the following...

# you need to set some environment variables just for populating the database using the python shell
export POSTGRES_USER='postgres'
export POSTGRES_PASSWORD='userPass'
export POSTGRES_DB='postgres'

# now begin to do the population step by running init_db within database.py
python
import os
user = os.environ['POSTGRES_USER']
pwd = os.environ['POSTGRES_PASSWORD']
db = os.environ['POSTGRES_DB']

import database
database.init_db()

# after a bit of waiting, the artists should be populated into a ./dbdata folder.
```

Now that the database has been initalized and populated, you can do the following
```
docker-compose up # spins up the db, nginx, and flaskapp

docker-compose down # spins down the db, nginx, and flaskapp
```
