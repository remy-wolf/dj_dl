import sys
import os
import string

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from ytmusicapi import YTMusic
# import yt_dlp

from download import download
from credentials import CLIENT_ID, CLIENT_SECRET


# get tracks from spotify playlist
def get_tracks(playlist_url, start=None, end=None):
    client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

    if not start:
        start = 0
    if not end:
        limit = 100
        total_tracks = None
    else:
        limit = end - start
        total_tracks = limit

    results = sp.playlist_tracks(playlist_url, fields="items(track(name, artists.name, duration_ms)), next", limit=limit, offset=start)
    tracks = []
    while results and (not total_tracks or len(tracks) < total_tracks):
        tracks.extend([t['track'] for t in results['items']])
        results = sp.next(results)

    return tracks


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
    if clean_version and not yt_result['isExplicit']: score += CLEAN_VERSION
    if yt_title in sp_title or sp_title in yt_title: score += TITLE_MATCH
    if yt_result['resultType'] == 'song': score += SONG_RESULT
    if yt_duration >= duration_min and yt_duration <= duration_max: score += DURATION_MATCH # allow small duration buffer
    if any (x in yt_title for x in RADIO_SEARCH_TERMS): score += RADIO_EDIT
    if 'music video' in yt_title: score += MUSIC_VIDEO
    return score


def search_yt(sp_tracks, search_for_extended_mix = False, search_for_clean_version = False):
    ytmusic = YTMusic()
    urls = []
    skipped = []
    for sp_track in sp_tracks:
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
            # artists = ', '.join([artist['name'].lower() for artist in yt_res['artists']])
            # title = yt_res['title']
            # url = f"www.youtube.com/watch?v={yt_res['videoId']}"
            # print(f"{artists} - {title} (score: {score}) (url: {url}).")
            if score > best_score:
                best_result = yt_res
                best_score = score
        if best_result:
            artists = ', '.join([artist['name'].lower() for artist in best_result['artists']])
            title = best_result['title']
            url = f"https://www.youtube.com/watch?v={best_result['videoId']}"
            print(f"Found {artists} - {title} (score: {best_score}) (url: {url}).")
            urls.append(url)
        else:
            print(f"No good video found for {partial} - skipping.")
            skipped.append(partial)
    return urls, skipped

def main():
    url=input("Enter playlist to download: ")
    extended=input("Search for extended mix? (Good for house/techno) (Y/N): ")
    clean=input("Search for clean version? (Y/N): ")
    start=input("Playlist start number (or hit enter to download from beginning of playlist): ")
    end=input("Playlist end number (or hit enter to download through end of playlist): ")

    search_for_extended_mix = len(extended) > 0 and extended[0].lower() == 'y'
    search_for_clean_version = len(clean) > 0 and clean[0].lower() == 'y'

    if len(start) == 0:
        start = None
    else:
        start = int(start) - 1 # because arrays are 0-indexed
    if len(end) == 0:
        end = None
    else:
        end = int(end) - 1

    tracks = get_tracks(url, start, end)
    urls, skipped = search_yt(tracks, search_for_extended_mix, search_for_clean_version)
    download(urls)
    skipped = ''.join(f"\n    {title}" for title in skipped)
    print(f"Videos skipped: {skipped}")
    print("Done.")


if __name__ == "__main__":
    main()