import spotipy
from spotipy.oauth2 import SpotifyOAuth
from collections import Counter

# Set your Spotify app credentials
CLIENT_ID = "70374e892e5c462fb285dc17095e8abd"
CLIENT_SECRET = "cd74889afd1240d3a13507f030f72372"
REDIRECT_URI = "http://localhost:8888/callback"

# Set the scope to read playback history
SCOPE = "user-top-read user-read-recently-played"

# Authenticate with Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=SCOPE))

# Function to get recently played tracks
def get_recently_played(limit=50):
    results = sp.current_user_recently_played(limit=limit)
    tracks = results['items']
    return [(track['track']['name'], track['track']['album']['name']) for track in tracks]

# Function to get top tracks or artists
def get_top_items(item_type="tracks", limit=10, time_range="medium_term"):
    if item_type == "tracks":
        results = sp.current_user_top_tracks(limit=limit, time_range=time_range)
        return [track['name'] for track in results['items']]
    elif item_type == "artists":
        results = sp.current_user_top_artists(limit=limit, time_range=time_range)
        return [artist['name'] for artist in results['items']]

# Analyze frequencies
def analyze_frequencies():
    recent_tracks = get_recently_played()
    track_counter = Counter([track for track, album in recent_tracks])
    album_counter = Counter([album for track, album in recent_tracks])
    
    print("\nMost Played Tracks:")
    for track, count in track_counter.most_common(5):
        print(f"{track}: {count} plays")
    
    print("\nMost Played Albums:")
    for album, count in album_counter.most_common(5):
        print(f"{album}: {count} plays")

# Main function
if __name__ == "__main__":
    print("Top Tracks:", get_top_items(item_type="tracks", limit=5))
    print("Top Artists:", get_top_items(item_type="artists", limit=5))
    analyze_frequencies()
