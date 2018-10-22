from spotipy.oauth2 import SpotifyClientCredentials
import spotipy

credentials = SpotifyClientCredentials('nickdelnano@gmail.com')
client = spotipy.Spotify(client_credentials_manager=credentials)
results = client.current_user_recently_played()    
