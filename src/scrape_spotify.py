import os
import string
import json

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from ytmusicapi import YTMusic

from download_youtube import download_youtube

# init spotipy
try:
    with open(os.path.join('config', 'secrets.json')) as f:
        secrets = json.load(f)
    client_credentials_manager = SpotifyClientCredentials(
        client_id=secrets['SPOTIPY_CLIENT_ID'], client_secret=secrets['SPOTIPY_CLIENT_SECRET']
    )
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
    sp.available_markets() # dummy call to see if auth worked correctly
except (
    FileNotFoundError, json.decoder.JSONDecodeError, KeyError, spotipy.oauth2.SpotifyOauthError
):
    print("ERROR: API credentials missing or incorrectly configured. Please ensure that "
          "config/secrets.json exists and contains the necessary credentials. Consult the "
          "documentation for more info.")
    exit()

# get tracks from spotify playlist
def get_playlist_tracks(playlist_url, start=None, end=None):
    if not start:
        start = 0
    if not end:
        limit = 100
        total_tracks = None
    else:
        limit = end - start
        total_tracks = limit

    playlist_name = sp.user_playlist(user=None, playlist_id=playlist_url, fields="name")['name']
    results = sp.playlist_tracks(playlist_url, fields="name, items(track(name, artists.name, duration_ms)), next", limit=limit, offset=start)
    tracks = []
    while results and (not total_tracks or len(tracks) < total_tracks):
        tracks.extend([t['track'] for t in results['items']])
        results = sp.next(results)

    return playlist_name, tracks


# used for scoring youtube results based on original spotify song
EXTENDED_MIX = 4
CLEAN_VERSION = 4
TITLE_MATCH = 3
SONG_RESULT = 1
DURATION_MATCH = 1
RADIO_EDIT = -2
MUSIC_VIDEO = -4
EXTENDED_SEARCH_TERMS = ['extended', 'original', 'club mix', 'club edit']
EXTENDED_IGNORE_TERMS = ['hour', 'hours', 'loop']
RADIO_SEARCH_TERMS = ['radio edit', 'radio mix', 'radio version']
REMIX_TERMS = ['remix', 'flip', 'mashup', 'bootleg']
# compare result from youtube based on expected result from spotify
def rank_video(yt_result, sp_result, extended_mix = False, clean_version = False):
    yt_artists = [artist['name'].lower() for artist in yt_result['artists']]
    sp_artists = [artist['name'].lower() for artist in sp_result['artists']]
    yt_title = yt_result['title'].lower().translate(str.maketrans('', '', string.punctuation)).replace('  ', ' ')
    sp_title = sp_result['name'].lower().translate(str.maketrans('', '', string.punctuation)).replace('  ', ' ')
    yt_title_terms = yt_title.split(' ')
    sp_title_terms = sp_title.split(' ')
    if yt_result['duration'] is None: return -10 # weird edge case
    yt_duration = yt_result['duration_seconds']
    sp_duration = sp_result['duration_ms'] / 1000
    duration_min = sp_duration - 5
    duration_max = sp_duration + 5
    if extended_mix:
        duration_max *= 2

    score = 0
    # TODO: wilkinson & sharleen hector edge case
    if not any (sp_artist in yt_artists or sp_artist in yt_title for sp_artist in sp_artists): return -1 # ignore results that don't have at least artist match
    if not sp_title_terms[0] in yt_title_terms: return -1 # ignore results that don't match at least part of the title
    if any ((term in yt_title_terms) != (term in sp_title_terms) for term in REMIX_TERMS): return -1 # ignore results that are remixes when they shouln't be, and vice versa
    if (extended_mix 
            and (any (x in yt_title for x in EXTENDED_SEARCH_TERMS) or yt_duration >= duration_min + 40)
            and not (any (x in yt_title for x in EXTENDED_IGNORE_TERMS))):
        score += EXTENDED_MIX
    if clean_version and yt_result['resultType'] == 'song' and not yt_result['isExplicit']: score += CLEAN_VERSION
    if yt_title in sp_title or sp_title in yt_title: score += TITLE_MATCH
    if yt_result['resultType'] == 'song': score += SONG_RESULT
    if yt_duration >= duration_min and yt_duration <= duration_max: score += DURATION_MATCH # allow small duration buffer
    if any (x in yt_title for x in RADIO_SEARCH_TERMS): score += RADIO_EDIT
    if 'music video' in yt_title: score += MUSIC_VIDEO
    return score


def search_yt(sp_track, search_for_extended_mix = False, search_for_clean_version = False):
    ytmusic = YTMusic()
    sp_artists = ', '.join([artist['name'] for artist in sp_track['artists']])
    sp_title = sp_track['name']
    
    partial = f"{sp_artists} - {sp_title}"
    search_term = partial
    if search_for_extended_mix:
        search_term = f"{search_term} Extended Mix"
    if search_for_clean_version:
        search_term = f"{search_term} Clean"
    print(f"Searching for {partial}...")
    yt_results = ytmusic.search(search_term, filter="songs")[:5]
    yt_results.extend(ytmusic.search(search_term, filter="videos")[:3])
    best_score = 0 # don't take videos with negative score
    best_result = None
    for yt_res in yt_results:
        score = rank_video(yt_res, sp_track, search_for_extended_mix, search_for_clean_version)
        if score > best_score:
            best_result = yt_res
            best_score = score
    if not best_result:
        print(f"No good match found for {partial} - skipping.")
        return partial, True

    artists = ', '.join([artist['name'].lower() for artist in best_result['artists']])
    title = best_result['title']
    url = f"https://www.youtube.com/watch?v={best_result['videoId']}"
    print(f"Found {artists} - {title} (score: {best_score}) (url: {url}).")
    return url, False


def handle_playlist(url, search_for_extended_mix = False, search_for_clean_version = False):
    start=input("Playlist start number (or hit enter to download from beginning of playlist): ")
    end=input("Playlist end number (or hit enter to download through end of playlist): ")

    if len(start) == 0:
        start = None
    else:
        start = int(start) - 1 # because arrays are 0-indexed
    if len(end) == 0:
        end = None
    else:
        end = int(end) - 1

    urls = []
    skipped = []
    playlist_name, tracks = get_playlist_tracks(url, start, end)
    print(f"\nSearching for matches on YouTube for tracks in '{playlist_name}'...\n")
    for track in tracks:
        url_or_title, skip = search_yt(track, search_for_extended_mix, search_for_clean_version)
        if skip:
            skipped.append(url_or_title)
        else:
            urls.append(url_or_title)
    print("\nDownloading tracks from YouTube...\n")
    download_youtube(urls, playlist_name)
    if len(skipped) > 0:
        skipped = ''.join(f"\n    {title}" for title in skipped)
        print(f"\nCould not find a high-quality match for the following tracks (and did not download): {skipped}")


def handle_track(url, search_for_extended_mix = False, search_for_clean_version = False):
    client_credentials_manager = SpotifyClientCredentials(client_id=secrets['SPOTIPY_CLIENT_ID'], client_secret=secrets['SPOTIPY_CLIENT_SECRET'])
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
    track = sp.tracks([url])['tracks'][0]
    url_or_title, skip = search_yt(track, search_for_extended_mix, search_for_clean_version)
    if skip:
        print(f"Could not find a high-quality match for {url_or_title} (and did not download).")
    else:
        download_youtube(url_or_title)


def scrape_spotify(url):
    extended=input("Search for extended mix? (Good for house/techno) (Y/N): ")
    clean=input("Search for clean version? (Y/N): ")
    search_for_extended_mix = len(extended) > 0 and extended[0].lower() == 'y'
    search_for_clean_version = len(clean) > 0 and clean[0].lower() == 'y'

    valid_url = False
    if 'playlist' in url:
        handle_playlist(url, search_for_extended_mix, search_for_clean_version)
        valid_url = True
    elif 'track' in url:
        handle_track(url, search_for_extended_mix, search_for_clean_version)
        valid_url = True
    else:
        print(f"ERROR: Cannot download tracks from the url: {url}")
        print("Only playlists or single tracks are currently supported.")
    return valid_url