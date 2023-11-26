from flask import Flask, jsonify
import numpy as np
import requests
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import pandas as pd
from sklearn.cluster import KMeans
import joblib
import os
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import euclidean
from flask_cors import CORS
from sklearn.preprocessing import StandardScaler
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
CORS(app)

client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SCERET')
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id, client_secret))

auth_token = None

def search_track(auth_token, song_name, artist_name):
    search_url = "https://api.spotify.com/v1/search"
    headers = {
        "Authorization": f"Bearer {auth_token}",
    }
    params = {
        "q": f"{song_name} {artist_name}",
        "type": "track",
    }

    response = requests.get(search_url, headers=headers, params=params)
    response_data = response.json()

    if "tracks" in response_data and "items" in response_data["tracks"] and response_data["tracks"]["items"]:
        return response_data["tracks"]["items"][0]
    else:
        return None

def get_album_artwork(track):
    if track and "album" in track and "images" in track["album"] and track["album"]["images"]:
        return track["album"]["images"][0]["url"]
    else:
        return None

def get_album_artworks(auth_token, songs):
    for song in songs:
        song_name, artist_name = song['song_title'], song['artist']
        track = search_track(auth_token, song_name, artist_name)
        artwork_url = get_album_artwork(track)
        
        song['artwork_url'] = artwork_url  

    return songs


def get_recommendations(input):
    df = pd.read_csv('labelled.csv')
    kmeans = joblib.load('kmeans_model.joblib')
    new_element_cluster = kmeans.predict(input)

    print("new_element_Cluster", new_element_cluster)

    same_cluster_df = df[df['cluster_label_kmeans'].isin(new_element_cluster)].copy()

    euclidean_distances = [euclidean(input.flatten(), x) for x in same_cluster_df.iloc[:, 0:10].values]

    same_cluster_df['euclidean_similarity'] = euclidean_distances

    similar_elements_df = same_cluster_df.sort_values(by='euclidean_similarity')

    top_7_similar_elements = similar_elements_df.iloc[1:10]

    selected_features = ['song_title', 'artist']
    songs = top_7_similar_elements[selected_features].to_dict(orient='records')

    return songs


@app.route('/<song>/<artist>')
def get_audio_features(song, artist):
    global auth_token

    try:
        if auth_token is None:
            auth_token = spotify.auth_manager.get_access_token(as_dict=False)

        headers = {'Authorization': f'Bearer {auth_token}'}

        params = {'q': f'{song} {artist}', 'type': 'track'}
        search_response = requests.get('https://api.spotify.com/v1/search', params=params, headers=headers)
        search_data = search_response.json()

        if 'tracks' not in search_data:
            raise ValueError("Unexpected API response format")

        if "tracks" in search_data and "items" in search_data["tracks"] and search_data["tracks"]["items"]:
            track_id = search_data["tracks"]["items"][0]["id"]
        else:
            return None

        audio_features = spotify.audio_features([track_id])[0]

        feature_names = [
            'acousticness', 'danceability', 'duration_ms', 'energy',
            'instrumentalness', 'liveness', 'loudness', 'speechiness',
            'tempo', 'valence'
        ]

        new_element_dict = {feature: audio_features[feature] for feature in feature_names}

        new_element_df = pd.DataFrame([new_element_dict])

        scaler = joblib.load('scaler_model.joblib')

        scaled_new_element = scaler.transform(new_element_df[feature_names])

        songs = get_recommendations(scaled_new_element.reshape(1, -1))

        artworks = get_album_artworks(auth_token, songs)

        return jsonify(artworks), 200  

    except requests.RequestException as request_error:
        print('Request Error:', request_error)
        return 'Spotify API Request Error', 503  

    except (ValueError, IndexError) as response_error:
        print('Error:', response_error)
        return 'Unexpected API Response Format', 500  

    except Exception as error:
        print('Error:', error)
        return 'Internal Server Error', 500


if __name__ == '__main__':
    app.run(port=3000)
