from flask import Flask, jsonify
import requests
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import pandas as pd
from sklearn.cluster import KMeans
import joblib
from sklearn.metrics.pairwise import cosine_similarity
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

client_id = 'c37c514dd8744f02aa005e01dd777410'
client_secret = '3e1c5009620b4c7d92baf0bac2658043'
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id, client_secret))

kmeans = None

import requests

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
    new_element_cluster = kmeans.predict([input])
    
    same_cluster_df = df[df['cluster_label_kmeans'].isin(new_element_cluster)].copy()  # Use copy() to avoid the warning

    similarity_scores = cosine_similarity([input], same_cluster_df.iloc[:, 2:12].values)[0]

    same_cluster_df['cosine_similarity'] = similarity_scores

    similar_elements_df = same_cluster_df.sort_values(by='cosine_similarity', ascending=False)
    
    top_7_similar_elements = similar_elements_df.iloc[1:10]  
    
    selected_features = ['song_title', 'artist']
    songs = top_7_similar_elements[selected_features].to_dict(orient='records')
    
    return songs

    
@app.route('/')
def train_model():
    df = pd.read_csv('SongDataset.csv')
    n_clusters = 5  
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    cluster_labels_kmeans = kmeans.fit_predict(df.iloc[:, 2:].values)

    df['cluster_label_kmeans'] = cluster_labels_kmeans
    joblib.dump(kmeans, 'kmeans_model.joblib')
    df.to_csv('labelled.csv', index=False) 
    return "WELCOME"
       

@app.route('/<song>/<artist>')
def get_audio_features(song, artist):
    try:
        auth_token = spotify.auth_manager.get_access_token(as_dict=False)

        headers = {'Authorization': f'Bearer {auth_token}'}

        params = {'q': f'{song} {artist}', 'type': 'track'}
        search_response = requests.get('https://api.spotify.com/v1/search', params=params, headers=headers)
        search_data = search_response.json()

        if 'tracks' not in search_data:
            raise ValueError("Unexpected API response format")

        first_track_id = search_data['tracks']['items'][0]['id']

        audio_features = spotify.audio_features([first_track_id])[0]
        
        new_element = [
            audio_features['acousticness'],
            audio_features['danceability'],
            audio_features['duration_ms'],
            audio_features['energy'],
            audio_features['instrumentalness'],
            audio_features['liveness'],
            audio_features['loudness'],
            audio_features['speechiness'],
            audio_features['tempo'],
            audio_features['valence']
        ]

        songs = get_recommendations(new_element)

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
