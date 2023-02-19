# dj_dl
Utilities for downloading .mp3 files, built using yt-dlp.

Please don't use this for commercial purposes thanks

Known issues/Future improvements:
* Some songs get renamed with weird Unicode characters, which show up as Chinese characters in Rekordbox.
* Matching Spotify to YouTube is not always perfect (and probably will never be)
* No checking if songs have already been downloaded
* No way to specify a date or offset for Spotify playlist download--entire playlist will be downloaded
* No Mac support (Python scripts work, but not batch files)
* No way to save options (search for extended mix/clean version?)
* No install script or update script--must install conda and binaries manually
