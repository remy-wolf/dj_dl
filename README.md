# dj_dl, v1.1
A tool to download Spotify or YouTube playlists while maintaining a consistent naming scheme. Built using yt-dlp, Spotipy, and ytmusicapi.
Please don't use this for commercial purposes!

Installation:
1) Ensure you have [git](https://git-scm.com/), [Python](https://www.python.org/), and [miniconda](https://docs.conda.io/projects/miniconda/en/latest/) or [anaconda](https://www.anaconda.com/) installed on your system
2) Clone this repo:\
`cd path/to/desired/directory && git clone https://github.com/april-manhattan/dj_dl.git`
3) Open the Anaconda prompt, navigate to the install directory, and run the following command to download the necessary Python dependencies:\
`conda env create -f lib_dl-env.yml`
4) Create a file named .env in src/ that contains the spotipy API keys
5) Double-click on DJ_DL.bat to run the application


Known issues/Future improvements:
* Some songs get renamed with weird Unicode characters, which show up as Chinese characters in Rekordbox.
* Matching Spotify to YouTube is not always perfect (and probably will never be)
* No checking if songs have already been downloaded
* No way to specify a date offset for Spotify playlist download (playlist number offset is currently supported)
* No Mac support (Python scripts work, but not batch files)
* No way to save options (search for extended mix/clean version?)
* No install script or update script--must install dependencies manually using conda
* Not all artists will always get included in the filename/ID3 tags
