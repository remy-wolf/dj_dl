# dj_dl, v1.1
A tool to download Spotify or YouTube playlists while maintaining a consistent naming scheme. Built using yt-dlp, Spotipy, and ytmusicapi.
Please don't use this for commercial purposes!

Installation:
1) Ensure you have [git](https://git-scm.com/) and [Python](https://www.python.org/), installed on your system
2) Clone this repo:
```
cd path/to/desired/directory && git clone https://github.com/remy-wolf/dj_dl.git
```
3) Create the virtual environment and install the requirements (commands are for Windows--installation will differ on MacOS):
```
python -m venv .venv --prompt dj_dl
.venv\Scripts\activate
python -m pip install -r requirements.txt
```
You might need to install ffmpeg/ffprobe separately.

4) Create a file named config\secrets.json that contains the Spotipy API keys
5) Double-click on DJ_DL.bat to run the application


Known issues/Future improvements:
* Some songs get renamed with weird Unicode characters, which show up as Chinese characters in Rekordbox.
* Matching Spotify to YouTube is not always perfect (and probably will never be)
* No checking if songs have already been downloaded
* No way to specify a date offset for Spotify playlist download (playlist number offset is currently supported)
* No Mac support (Python scripts work, but not batch files)
* No way to save options (search for extended mix/clean version?)
* No install script or update script--must install dependencies manually
* Not all artists will always get included in the filename/ID3 tags
