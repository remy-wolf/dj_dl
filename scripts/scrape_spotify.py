import sys
import os

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp

from download import download
from credentials import CLIENT_ID, CLIENT_SECRET


INCLUDE_EXTENDED_MIX = True
NUM_ENTRIES = 3


def main():
    url = sys.argv[1]

    client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

    playlist = sp.playlist_tracks(url, fields="items(track(name, artists.name))")['items']

    ydl_opts = {
        'format': 'mp3/bestaudio/best',
        'quiet': True,
    }

    urls = []
    skipped = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for song in playlist:
            song = song['track']
            artists = ', '.join([artist['name'] for artist in song['artists']])
            title = song['name']
            partial = f"{artists} - {title}"
            search_term = partial
            if INCLUDE_EXTENDED_MIX:
                search_term = f"{search_term} (Extended Mix)"
            print(f"Searching for {partial}...")
            # TODO: use youtube music search exclusively?
            videos = ydl.extract_info(f"ytsearch{NUM_ENTRIES}:{search_term}", download=False)
            found = False
            for entry in videos['entries']:
                print(f"Found {entry['title']} (url: {entry['original_url']}).")
                correct = input("Correct video? Hit enter or type 'y' if so: ")
                if (correct == '' or correct[0].lower() == 'y'):
                    urls.append(entry['original_url'])
                    found = True
                    break
            if not found:
                print(f"Skipping {partial}.")
                skipped.append(partial)
    
    download(urls)
    skipped = [f"\n    {title}" for title in skipped]
    print(f"Videos skipped: {skipped}")


if __name__ == "__main__":
    main()