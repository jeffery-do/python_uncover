## Build Graphlab Docker container with below...
Install reference:
https://curtisz.com/dockerized-ipython-and-graphlab-create-for-ml-2/


docker build -t=graphlab --build-arg "USER_EMAIL=jedo@calpoly.edu" --build-arg "USER_KEY=10BA-7EE6-9E18-EF9D-AF04-45C4-FD60-A4CD" .


# To init_db:

docker-compose up db # spin up your database


```
# you will not populate your postgres database...

# you must export the following env variables:
user = os.environ['POSTGRES_USER']
pwd = os.environ['POSTGRES_PASSWORD']
db = os.environ['POSTGRES_DB']

example... # follow your env_file but convert lines to normal exports
export POSTGRES_PASSWORD='userpass'

# followed with running initailization script
python
$ import database
$ database.init_db()

```
