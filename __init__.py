from flask import Flask
from flask import render_template
from flask import request
from flask import flash
from flask import session
from flask import Response
from flask_oauthlib.client import OAuth, OAuthException
from sqlalchemy import inspect
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import logging
import glob
import os
import functools
import csv
import threading
import random
import turicreate as tc
import numpy as np
import collections
import pandas as pd
import traceback
import ticketmaster

app = Flask(__name__)
app.secret_key = 'A_great_secRet_KeyyyYy'

app.config["USERNAME"] = "admin"
app.config["PASSWORD"] = "password"
app.config["TEMPLATES_AUTO_RELOAD"] = True

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

lock = threading.Lock()

spot = None

TEMPLATES_AUTO_RELOAD = True

# SPOTIFY_APP_ID
with app.app_context():
    from spotify import spotify_page
    # app = Flask(__name__)
    # spot = gen_spotify_oauth()
    # app.spotify = spot
    app.register_blueprint(spotify_page)

from models import dbArtists, dbUsers, dbRatings, dbConcerts
from database import db_session, db_engine
# from flask_sqlalchemy import SQLAlchemy

# ---------

# Auth

# design docs need to be written...
# like actually now that I have the appropraite
# data from spotify
# I can now combine my datasets
# using some form of distance metric
# I can go and cateogrize my data
# I'm thinking I should srink my dataset
# and clean it for POC purposes
# And in doing so, make it easier
# to make everything look nice
# After I do some formatting
# I should have recommended artists
# with their photos
# With something like that, I believe it's all appropriate.
# another day...
# it wouldn't be that bad to create a page that organizes
# the spotify data so that it's easier to act
# on it's data
# Yep make sure!

# hehe I'm opening some more stuff here...
# I really should get some work in... I'm already
# past the deadline I've set for myself
# but now it's funny. It seems like I'm actually going
# to do this now... Wierd how that happens...

def ok_user_and_password(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == app.config['USERNAME'] and password == app.config['PASSWORD']

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_authorization(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not ok_user_and_password(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
# ----------

# Uploading ----------
import os
from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename

dbConnection = None

def object_as_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}

class Ratings:
    def __init__(self):
        self.data = {}
        self.assignmentIter = {}
        exists = db_session.query(dbRatings.ratingid).first()
        if exists is not None:
            rows = dbRatings.query.all()
            for row in rows:
                d = object_as_dict(row)
                logger.debug('reading db ratingid: {}, user:{}, artist:{}, rating:{}'.format(d['ratingid'], d['userid'], d['artistid'], d['rating']))
                self.data[d['ratingid']] = self.genItem(
                    d['ratingid'],
                    d['userid'],
                    d['artistid'],
                    d['rating'])
        logger.debug('ALL RATINGS {}'.format(self.data))
    def genItem(self, ratingid, userid, artistid, rating):
        return {"ratingid":ratingid, "userid":userid, "artistid":artistid, "rating":rating}
    def add_rating(self, userid, artistid, ratingid, rating):
        self.data[ratingid] = self.genItem(ratingid, userid, artistid, rating)
    # def add_rating(self, userid, artist_name, rating):
    #     logger.debug("Entering add_rating in Ratings class: user_name:{} artist:{} rating:{}".format(userid, artist, rating))
    #     if rating != "none":
    #         aid = artist_name_to_aid(artist_name)
    #         logger.debug("| artist:{} found aid:{}".format(artist_name, aid))
    #         self.data[aid] = int(rating)

NONE = 'none'

# login for user
class User:
    def __init__(self,username):
        self.ratings = {}
        # self.userid = userid
        self.username = username
        # no longer needs to specify userid ... (will generate as needed)
        # check if username exists.
        #   If so, use user id... get user ratings...
        #   If not, insert into db...
        exists = db_session.query(dbUsers.name).first()
        USERFOUND = False
        if exists is not None:
            rows = dbUsers.query.all()
            for row in rows:
                d = object_as_dict(row)
                logger.debug('Read userid:{}, name:{}'.format(d['userid'], d['name']))
                if d['name'] == self.username:
                    logger.debug('We found the user! userid:{}, name:{}'.format(d['userid'], d['name']))
                    self.userid = d['userid']
                    # need to get all ratings ...
                    self.ratings = self.get_db_ratings(self.userid)
                    USERFOUND = True
        if USERFOUND == False:
            aUser = dbUsers(name=self.username)
            db_session.merge(aUser)
            db_session.commit()
            self.userid = aUser.userid
        logger.debug('initalized userid {}, username {} ratings: {}'.format(self.userid, self.username, self.ratings))
    def get_db_ratings(self, userid):
        exists = db_session.query(dbRatings.ratingid).first()
        results = {}
        if exists is not None:
            # pull data from db...
            # rows = db_session.query(dbAssignments).all()
            rows = dbRatings.query.all()
            for row in rows:
                d = object_as_dict(row)
                if d['userid'] == userid:
                    results[d['artistid']] = d['rating']
        logger.debug('User {}, Available Ratings: {}'.format(userid, results))
        return results
    def get_ratings(self, artists):
        result = []
        for artist in artists:
            if artist not in self.ratings:
                result.append(0)
            else:
                result.append(ratings[aritst])
        return result
    def add_rating(self, artist, rating):
        logger.debug("Entering add_rating: artist:{} rating:{}".format(artist, rating))
        if rating != "none":
            aid = artist_name_to_aid(artist)
            logger.debug("| artist:{} found aid:{}".format(artist, aid))
            self.ratings[aid] = int(rating)
    def show_all_ratings(self):
        return self.ratings
    def show_all_ratings_by_name(self):
        result = {}
        for key,value in self.ratings.items():
            result[gartists.get_artist_with_id(key)] = value
        return result
    def get_userid(self):
        return self.userid
    def get_username(self):
        return self.username
    def upload_ratings(self):
        USERFOUND = False
        # check if user exists, if not upload user...
        exists = db_session.query(dbUsers.name).first()
        if exists is not None:
            rows = dbUsers.query.all()
            for row in rows:
                d = object_as_dict(row)
                logger.debug('Read userid:{}, name:{}'.format(d['userid'], d['name']))
                if d['name'] == self.username:
                    # we found the user! Do nothing...
                    USERFOUND = True
        if USERFOUND == False: # if user not found, must add user to DB
            aUser = dbUsers(name=self.username)
            db_session.merge(aUser)
            db_session.commit()
        # upload ratings
        for artistid, rating in self.ratings.items():
            logger.debug("Attempting to upload userid:{} artistid:{} rating:{}".format(self.userid, artistid, rating))
            try:
                aRating = dbRatings(userid=self.userid, artistid=artistid, rating=rating)
                db_session.merge(aRating, load=True)
                db_session.commit()
                tot_ratings.add_rating(self.userid, artistid, aRating.ratingid, rating)
            except Exception as e:
                traceback.print_exc()

class Artist:
    def __init__(self, name, id):
        self.artistname = name
        self.artistid = id
    def get_artistid(self):
        return self.artistid
    def send_to_db(self):
        try:
            aArtist = dbArtists(name=self.artistname)
            db_session.merge(aArtist)
            db_session.commit()
        except Exception as e:
            traceback.print_exc()

def artist_name_to_aid(name):
    return gartists.get_artist_with_name(name)

def aid_to_artist_name(aid):
    return gartists.get_artist_with_id(aid)

# artist_counter = 1;
class Artists:
    def __init__(self):
        pass
    def read_csv(self, file_name):
        self.data = collections.OrderedDict()
        self.artist_map = {}
        self.name_map = {}
        with open(file_name) as csvfile:
            df = pd.read_csv(file_name, header=0)
            for row in df[['id','name']].iterrows():
                name = str(row[1][1]).strip()
                id = row[0]
                self.data[name] = Artist(name,id)
                self.artist_map[id] = name
                self.name_map[name] = id
    def get_items(self):
        return self.data.items()
    def get_artists(num):
        x = []
        while len(x) < num:
            choice = random.choice(self.get_items())
            if choice[0] not in x:
                x.append(choice[0])
        return x
    def get_artist_with_id(self, id):
        return self.artist_map[id]
    def get_artist_with_name(self, name):
        return self.name_map[name]
    def sent_to_db(self):
        logger.debug("Sending Artists to db")
        counter = 0 # TODO add in counter to keep track of new artists
        for key, val in self.data.items():
            val.send_to_db()


def init_gartists():
    global gartists
    gartists = Artists()
    gartists.read_csv("./data/artists_p.csv")
    gartists.sent_to_db()

def get_artists(num):
    x = []
    while len(x) < num:
        choice = random.choice(list(gartists.get_items()))
        if choice[0] not in x:
            x.append(choice[0])
    return x

users = {}
userIdCounter = 1000
def get_user_by_userid(userid):
    return users[userid]
def get_user(username):
    for key,value in users.items():
        if username == value.get_username():
            logger.debug("Get user info of user: {}".format(value))
            return value
    return None

def set_user(username):
    global userIdCounter
    global user
    global users
    try:
        user = User(username)
        users[user.userid] = user
        return users[user.userid]
    except:
        traceback.print_exc()
        logger.debug("ROLLBACK Occured!!!")
        db_session.rollback()
        set_user(username)

def get_default_ratings(user, artists):
    return user.get_ratings(artists)

def init_default_user():
    set_user("default_user")

@app.route("/")
def index():
    if "USER_NAME" not in session.keys():
        set_user("default_user")
        session["USER_NAME"] = "default_user"
    return render_template('index.html')

@app.route("/preferences", methods=["GET", "POST"])
def preferences():
    global user
    logger.debug("HERE IS ALL CURRENT USER INFO: {}".format(users))
    if "USER_NAME" not in session.keys():
        user=set_user("default_user")
        session["USER_NAME"] = "default_user"
    user = get_user(session['USER_NAME'])
    if request.method == 'POST':
        if "USER_NAME" in request.form.keys():
            session['USER_NAME'] = request.form["USER_NAME"]
            user=set_user(request.form["USER_NAME"])
        else:
            logger.debug("Request Form: {}".format(request.form))
            userid = user.get_userid()
            for key,value in request.form.items():
                if key != "USER_NAME":
                    res = [x.strip() for x in key.split('rating-')]
                    artist_name = ''.join(res[1:])
                    user.add_rating(artist_name,value)
            logger.debug("All ratings: {}".format(user.show_all_ratings()))

    # Generate 5 artists
    artists = get_artists(5)
    logger.debug("Generated these artists: {}".format(artists))
    default_ratings = get_default_ratings(user,artists)
    all_ratings = user.show_all_ratings_by_name()
    # 5 rating boxes
    # show boxes in order, and send to screen
    concerts = ticketmaster.get_concerts_for_artists(artists, tm_collection)
    logger.debug("concerts found on ticketmaster {}".format(concerts))
    print 'all_ratings: ', all_ratings
    all_rating_artists = [a for a,r in all_ratings.items()]
    all_rating_concerts = ticketmaster.get_concerts_for_artists(all_rating_artists, tm_collection)
    return render_template('preferences.html', artist_ratings=zip(artists, default_ratings), all_ratings=all_ratings, current_user=session["USER_NAME"], concerts=concerts, all_rating_concerts=all_rating_concerts)

@app.route("/recommendations")
def recommendations():
    if "USER_NAME" not in session.keys():
        set_user("default_user")
        session["USER_NAME"] = "default_user"
    # sf = tc.SFrame.read_csv("./data/ratings.csv")
    logger.debug("Making recommendation using user: {}".format(session['USER_NAME']))
    sf = ratings_to_sframe(tot_ratings)
    sf = sf.remove_column('ratingid')
    print "TOTAL SF"
    print sf
    user = get_user(session['USER_NAME'])
    if len(user.show_all_ratings()) > 0:
        # user_rating_artists = [artist_name_to_aid(key) for key in user.show_all_ratings().keys()]
        user_rating_artists , user_rating_rating = zip(*user.show_all_ratings().items())
        # user_rating_rating = user.show_all_ratings().values()
        my_sf = tc.SFrame({'rating':user_rating_rating, 'userid':([user.get_userid()]*len(user_rating_artists)), 'artistid':user_rating_artists})
        print "MY SF"
        print my_sf
        sf = sf.append(my_sf)
        print "RESULTING SF"
        print sf
        m = tc.item_similarity_recommender.create(sf, target='rating', user_id='userid', item_id='artistid')
        recs = m.recommend(users=[user.get_userid()],k=5,verbose=True)
        print(recs)
        list_recs = [aid_to_artist_name(x) for x in recs['artistid']]

        concerts = ticketmaster.get_concerts_for_artists(list_recs, tm_collection)
        logger.debug("concerts found on ticketmaster {}".format(concerts))
        return render_template('recommendations.html', list_recs=list_recs, concerts=concerts, empty=False)
    else:
        return render_template('recommendations.html', empty=True)


def find_concerts():
    exists = db_session.query(dbConcerts.concertid).first()
    concert_list = []
    if exists is not None:
        rows = dbRatings.query.all()
        for row in rows:
            d = object_as_dict(row)
            logger.debug('reading dbConcerts: concertid: {}, concertname:{}, artists:{}, url:{}'.format(d['concertid'], d['concertname'], d['artists'], d['url']))
            concert_list.append(d)
    return concert_list

@app.route("/concerts")
def concerts_page():
    concerts = find_concerts()
    if concerts != []:
        return render_template('concerts.html', concerts=concerts, empty=False)
    else:
        return render_template('concerts.html', empty=True)


@app.route("/reload_ticketmaster")
def reload_ticketmaster():
    global tm_collection
    tm_collection = ticketmaster.collect_activities(0,5)

def ratings_to_sframe(ratings):
    vals = list(ratings.data.values())
    res = {}
    keys = vals[0].keys()
    for x in keys:
        res[x] = []
    for dict_rating in vals:
        for key in keys:
            res[key].append(dict_rating[key])
    return tc.SFrame(res)


@app.route("/save_user")
def save_user():
    logger.debug("Attempting to save user info")
    # saving session user
    user = get_user(session['USER_NAME'])
    user.upload_ratings()
    return render_template('save_confirmation.html', user=session['USER_NAME'], ratings=user.show_all_ratings_by_name())

@app.route("/reset_ratings")
def reset_ratings():
    logger.debug("Attempting reset")
    db_session.query(dbRatings).delete()
    db_session.commit()
    return redirect(url_for('index'))

@app.route("/logout")
def logout():
    logger.debug("Attempting logout")
    session.clear()
    return redirect(url_for('index'))

# @app.route("/spotify_login")
# def spotify_login():
#     callback = url_for(
#         'spotify_authorized',
#         next=request.args.get('next') or request.referrer or None,
#         _external=True
#     )
#     return spot.authorize(callback=callback)
#
# @app.route('/login/authorized')
# def spotify_authorized():
#     resp = spot.authorized_response()
#     if resp is None:
#         return 'Access denied: reason={0} error={1}'.format(
#             request.args['error_reason'],
#             request.args['error_description']
#         )
#     if isinstance(resp, OAuthException):
#         return 'Access denied: {0}'.format(resp.message)
#
#     session['oauth_token'] = (resp['access_token'], '')
#     me = spot.get('/me')
#     return 'Logged in as id={0} name={1} redirect={2}'.format(
#         me.data['id'],
#         me.data['name'],
#         request.args.get('next')
#     )
#
# @spot.tokengetter
# def get_spotify_oauth_token():
#     return session.get('oauth_token')

if __name__ == "__main__":
    init_gartists()
    init_default_user()
    tot_ratings = Ratings()
    reload_ticketmaster()
    print("APPLICATION IS READY")
    app.run(host="0.0.0.0", port=5090)
