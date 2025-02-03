import os
import re


DIR = "..\dj"

TRIM_WORDS = [
    "lyric", "lyrics", "video", "videoclip", "audio", "dir", "dir.", "directed", "visualizer", "vizualiser", "hq", "hd", "art",
    "monstercat", "electronic", "future bass", "garage", "house", "indie dance", "hard dance", "nu disco", "trap", "glitch hop", "dubstep", "edm",
    "owsla", "records", "ukf", "ultra music",
    "out now", "release", "official", "free", "download", "premiere",
    "ep", "lp", "album"
]

REPLACE_WORDS = [
    ("feat.", "ft."),
    ("Feat.", "ft."),
    ("FEAT.", "ft."),
    ("Ft.", "ft."),
    ("Featuring", "ft."),
    ("featuring", "ft."),
    ("Prod.", "prod."),
    ("Prod. by", "prod."),
    ("prod. by", "prod."),
    ("prod by", "prod."),
    ("Prod by", "prod.")
]


# checks the parenthetical/bracketed segment against TRIM_WORDS to see if this should be included or not
def check_segment(segment):
    # add leading and trailing space to allow us to ensure trim word does not occur within other word
    segment = (' ' + segment + ' ').lower()
    for trim_word in TRIM_WORDS:
        loc = segment.find(trim_word)
        if loc > 0:
            # make sure trim word doesn't occur within middle of other word
            if segment[loc-1] == ' ' and segment[loc + len(trim_word)] == ' ':
                return False
    return True


# match contents inside parens/square brackets
pattern = re.compile(r"[\(\[](?P<content>.*)?[\)\]]")

def get_new_name(filename):
    basename = os.path.basename(filename)
    dirname = os.path.dirname(filename)
    new_name = ""
    substring = basename

    # check for TRIM_WORDS
    while len(substring) > 0:
        m = pattern.search(substring) # search for anything in parens/square brackets
        if m:
            # bounds of parenthesized segment
            begin = m.span()[0]
            end = m.span()[1]
            # add everything before parenthesized segment
            new_name += substring[:begin]
            if check_segment(m.group('content')):
                # if segment does not contain any TRIM_WORDS, add it to the name
                new_name += substring[begin:end]
            substring = substring[end:]
        else:
            new_name += substring
            substring = ""
 
    # replace feat. with ft. and any other variations
    for replace_pair in REPLACE_WORDS:
        new_name = new_name.replace(replace_pair[0], replace_pair[1], 1)  

    # remove extra spaces and potential leading "-" character
    split = new_name.split()
    if split[0] == "-":
        split = split[1 : len(split)]

    # don't add space between last char and file extension
    if (split[len(split) - 1][0] == "."):
        new_name = " ".join(split[0 : len(split) - 1])
        new_name = new_name + split[len(split) - 1]
    else:
        new_name = " ".join(split[0 : len(split)]) 

    # strip leading and ending whitespace
    new_name = new_name.strip()  
    
    # if we have any changes, return them
    new_name = os.path.join(dirname, new_name)
    if new_name != filename:
        return new_name

    return None
        

def name_strip(directory): 
    for file in os.listdir(directory):
        full_name = os.path.join(directory, file) 
        # recursively enter directories
        if (os.path.isdir(full_name)):
            name_strip(full_name)
        else:
            new_name = get_new_name(full_name)
            if new_name:
                try:
                    os.rename(full_name, new_name)
                    print(f"Renamed {full_name}")
                except UnicodeEncodeError:
                    print("Renamed song with non-English characters")


def main():
    directory = os.path.join(os.getcwd(), DIR)
    name_strip(directory)


if __name__ == "__main__":
    main()
