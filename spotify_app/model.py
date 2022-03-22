import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

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


