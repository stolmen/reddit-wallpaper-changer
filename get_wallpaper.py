__author__ = 'ed'

import praw
import pprint
import re
import ctypes
import urllib
import os

SUPPORTED_EXTENSIONS = (".jpg", ".png")
DEFAULT_EXTENSION = ".jpg"

def test_parse_url():
    #print(parse_url(r"http://i.imgur.com/IC8Oa5T.png"))
    assert parse_url("http://imgur.com/asdf") == "http://imgur.com/asdf.jpg"
    assert parse_url("http://i.imgur.com/asdf") == "http://i.imgur.com/asdf.jpg"
    assert parse_url("penis") is False
    assert parse_url("penis.jpg") is False
    assert parse_url("http://imgur.com/asdf.jpg") == "http://imgur.com/asdf.jpg"
    assert parse_url("http://i.imgur.com/asdf.jpg") == "http://i.imgur.com/asdf.jpg"
    assert parse_url("http://imgur.com/a/asdf") is False
    assert parse_url("http://i.imgur.com/asdf.png") == "http://i.imgur.com/asdf.png"


def parse_url(url):
    match_obj = re.match("^http://(i.)?imgur.com/(\w)*(?P<extension>\.jpg|\.png)?$", url)
    if match_obj:
        # URL looks good. Now add the extension if required.

        if match_obj.group("extension") is None:
            # No extension. Append the default extension.
            url += DEFAULT_EXTENSION
        elif match_obj.group("extension") not in SUPPORTED_EXTENSIONS:
            url = False
    else:
        # Crap url. Return False.
        url = False

    return url


def change_wallpaper(fullpath):
    ctypes.windll.user32.SystemParametersInfoW(20, 0, fullpath, 0)

if __name__ == '__main__':

    test_parse_url()

    IMAGE_LOCATION = r"E:\pics\reddit_wallpaper_auto\\"
    # Connect to reddit
    user_agent = "Stolmen's Reddit Wallpaper grabber"
    print("Connecting to reddit")
    r = praw.Reddit(user_agent=user_agent)

    # Create subreddit
    name_of_subreddit = "wallpapers"
    the_subreddit = r.get_subreddit(subreddit_name=name_of_subreddit)

    # Grab the newest submission only
    top_post = the_subreddit.get_new(limit=25)
    found = False

    for ele in top_post:

        image_url = parse_url(ele.url)
        if image_url is not False:
            found = True
            pprint.pprint(vars(ele))
            break

    if found:
        image_filename = IMAGE_LOCATION + image_url.split(r"/")[3]

        if not os.path.isfile(image_filename):
            print("Downloading %s..." % image_url)
            urllib.request.urlretrieve(image_url, image_filename)
        else:
            print("It already exists! Not downloading after all..")

        change_wallpaper(image_filename)
    else:
        # In the unlikely event that no suitable URL is found,
        # throw some sort of error here.
        print("No suitable URL found. No wallpaper will be changed!")