'''This is the main app file. If time allows, we can make it more modular.
For now though, this is where everything goes.'''
# to load in the environment variables
from dotenv import load_dotenv
# the API library (we'll be using the df as a base, so don't worry too
# much about it.)
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

# useful datatype- defaultdicts don't throw key errors.
from collections import defaultdict
import pandas as pd

load_dotenv()
APP = Flask(__name__)
db = SQLAlchemy(APP)
APP.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASEURI")

# load the .env file and return credentials
def return_credentials():
    '''This function will pull the credentials from the .env
    file and return them. The redirect uri is set to the
    localhost.'''
    client_id = os.getenv("CLIENTID")
    client_secret = os.getenv("CLIENTSECRET")
    redirect_uri = "http://localhost:5000/"
    return client_id, client_secret, redirect_uri

# creates a cursor object, taking in credentials as parameters
def create_cursor(client_id, client_secret, redirect_uri):
    '''This function makes a cursor for us to get data from the api
    and defines the scope (can be adjusted according to project
    needs). This returns the cursor object.'''
    sp = spotipy.Spotify(auth_manager = SpotifyOAuth(client_id = client_id,
        client_secret = client_secret, redirect_uri = redirect_uri,
        scope = "user-read-recently-played"))
    return sp

def epic_predictor(input_track_key):

  ## Convert "input_track_key" to the index of the song (the song's position
  ## in the dataframe).
  # imports data to a dataframe from the csv
  data = pd.read_csv("https://raw.githubusercontent.com/Lambda-Spotify-Song-Suggester-3/datascience/master/kaggle_data/encoded.csv")
  df = data.copy()
  dictionary = df[["artist_name", "track_name", "track_key", "track_id"]]
  # Drop
  df = df.drop(columns=['artist_name','track_id', 'track_name','track_key', 'duration_ms', 'mode', 'loudness', 'time_signature'])
  # Scale the data
  scaler = StandardScaler()
  # the scaled dataframe
  df_s = scaler.fit_transform(df)

  input_dictionary_entry = dictionary[dictionary['track_key']==input_track_key]
  input_index = input_dictionary_entry.index[0]

  ## Nearest Neighbors model
  nn = NearestNeighbors(n_neighbors=10, algorithm='kd_tree')
  nn.fit(df_s)

  neighbor_predictions = nn.kneighbors([df_s[input_index]])

  ## This is a list of the INDEXES of the songs
  list_of_predictions = neighbor_predictions[1][0].tolist()

  ten_similar_tracks = []
  for item in list_of_predictions:
    track_hash = dictionary['track_id'].iloc[item]
    ten_similar_tracks.append(track_hash)

  return ten_similar_tracks

# query function for missing songs
def find_song(name, year):
    '''Fetches a song from the API and saves it to a database'''
    song_data = defaultdict()
    '''here we execute a request to the api with the spotipy
    search function. The q parameter accepts a string and can
    be one of the following values: album, track, year,
    upc, tag:hipster, tag:new, isrc, and genre.'''
    # pull the creds
    client_id, client_secret, redirect_uri = return_credentials()
    # create the cursor
    sp = create_cursor(client_id, client_secret, redirect_uri)
    # launch the search and save it to the variable results
    results = sp.search(q = "track: {} year: {}".format(name, year), limit = 1)
    # if null, nothing is returned
    if results["tracks"]["items"] == []:
        return None
    # results is made into a dictionary, which can be indexed
    results = results["tracks"]["items"][0]
    # song id is pulled
    id = results["id"]
    # now we use the song's id to query for audio features
    audio_features = sp.audio_features(id)[0]
    song_data['name'] = [name]
    song_data['year'] = [year]
    song_data['explicit'] = [int(results['explicit'])]
    song_data['duration_ms'] = [results['duration_ms']]
    song_data['popularity'] = [results['popularity']]
    for key, value in audio_features.items():
        song_data[key] = value

    return pd.DataFrame(song_data).to_csv("song_data.csv")

# main route
@APP.route("/")
def main():
    track_key = int(request.args["track_key"])
    return str(epic_predictor(track_key))