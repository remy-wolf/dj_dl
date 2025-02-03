from download_youtube import download_youtube
from scrape_spotify import scrape_spotify

def main():
    print("DJ DL, version 1.1")
    
    while True:
        url = input("\nEnter track or playlist to download (Spotify/YouTube supported): ")
        if 'youtube' in url or 'youtu.be' in url:
            print("YouTube link detected, downloading video/playlist...\n")
            download_youtube(url)
            valid_url = True
        elif 'spotify' in url:
            print("Spotify link detected, will search on YouTube for equivalent tracks.\n")
            valid_url = scrape_spotify(url)
        else:
            print("ERROR: Unrecognized link. Only YouTube and Spotify links are supported currently.")
            valid_url = False
        if valid_url:
            print("\nFinished. You can find your tracks in the Downloads folder in this directory.")

if __name__ == "__main__":
    main()