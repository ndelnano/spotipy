from spotipy.oauth2 import SpotifyClientCredentials
import spotipy

user_id = 14 # stub
credentials = SpotifyClientCredentials(user_id)
sp = spotipy.Spotify(client_credentials_manager=credentials)

results = sp.current_user_recently_played()
print(results)
for i in results['items']:
    print(i['track']['name'])
    print(i['played_at'])
