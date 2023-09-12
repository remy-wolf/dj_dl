import os
import sys

import yt_dlp
from yt_dlp.postprocessor.common import PostProcessor
from yt_dlp.utils import PostProcessingError

from name_strip import get_new_name
from update_tags import write_tags


class RenameAndWriteTagsPP(PostProcessor):
    def __init__(self, downloader=None, **kwargs):
        super().__init__(downloader)
        self._kwargs = kwargs
        
    def run(self, info):
        if info.get('filepath'):  # PP was called after download (default)
            filepath = info.get('filepath')

            # add artist name if missing
            contents = os.path.basename(filepath).split(" - ")
            if len(contents) >= 3:
                if contents[1] == 'Topic':
                    del contents[1] # if downloading from 'Topic' channel, remove 'Topic' and use uploader name as artist
                else:
                    del contents[0] # otherwise, remove uploader name
            filename = " - ".join(contents)
            
            filename = os.path.join(os.path.dirname(filepath), filename)

            # prefer this unicode colon
            filename = filename.replace('：', '꞉')

            # rename file, remove unwanted words
            new_name = get_new_name(filename)
            if new_name:
                filename = new_name

            try:
                os.rename(filepath, filename)
                self.to_screen(f"Renamed {filepath} to {filename}")
            except UnicodeEncodeError:
                self.to_screen("Renamed song with non-English characters")
            except FileExistsError:
                self.to_screen(f"Possible duplicate: {filepath}, cannot rename")

            # write id3 tags
            if write_tags(filename):
               raise PostProcessingError(f"Could not read tags of {filename}")
            else:
                self.to_screen("Updated id3 tags.")
            
        else:
            raise PostProcessingError("Post processor called at wrong time")
        
        return [], info  # return list_of_files_to_delete, info_dict


def download(urls):
    ydl_opts = {
        'format': 'mp3/bestaudio/best',
        'extractaudio': True,
        'writethumbnail': True,
        'allow_playlist_files': False,
        'outtmpl': os.path.join('Downloads', '%(playlist_title|)s', '%(uploader)s - %(title)s.%(ext)s'),
        'postprocessors': [
            {  
                # Extract audio using ffmpeg
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            {'key': 'EmbedThumbnail'},
        ]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.add_post_processor(RenameAndWriteTagsPP())
        error_code = ydl.download(urls)


def main():
    download(sys.argv[1:])


if __name__ == "__main__":
    main()