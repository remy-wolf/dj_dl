import os
from mutagen.easyid3 import EasyID3
from mutagen.id3._util import ID3NoHeaderError


DIR = "..\dj"


def write_tags(file):
    try:
        audio = EasyID3(file)
        basename = os.path.basename(file)
        # try to split artist and song title, remove extension
        split_artist = os.path.splitext(basename)[0].split(" - ", 1)
        if (len(split_artist) > 1):
            audio['artist'] = split_artist[0]
            audio['title'] = split_artist[1]
        else:
            audio['title'] = split_artist[0]
        audio.save()
        return False

    except ID3NoHeaderError:
        return True


def update_tags(directory): 
    for file in os.listdir(directory):
        full_name = os.path.join(directory, file) 
        # recursively enter directories
        if (os.path.isdir(full_name)):
            update_tags(full_name)
        else:
            err = write_tags(full_name)
            if err:
                print(f"Could not read tags of {file}")


def main():
    directory = os.path.join(os.getcwd(), DIR)
    update_tags(directory)


if __name__ == "__main__":
    main()
