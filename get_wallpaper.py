__author__ = 'ed'

import praw
import pprint
import re
import ctypes
import urllib
import os


def test_parse_url():
    assert parse_url("http://imgur.com/asdf") == "http://imgur.com/asdf.jpg"
    assert parse_url("http://i.imgur.com/asdf") == "http://i.imgur.com/asdf.jpg"
    assert parse_url("penis") is False
    assert parse_url("penis.jpg") is False
    assert parse_url("http://imgur.com/asdf.jpg") == "http://imgur.com/asdf.jpg"
    assert parse_url("http://i.imgur.com/asdf.jpg") == "http://i.imgur.com/asdf.jpg"
    assert parse_url("http://imgur.com/a/asdf") is False


def parse_url(url):
    if re.match("^http://(i.)?imgur.com/(\w)*(\.jpg)?$", url):
        # URL looks good. Now add the extension if required.
        if not re.match("^(.*)\.jpg$", url):
            url += ".jpg"
        return url
    else:
        return False


def change_wallpaper(fullpath):
    ctypes.windll.user32.SystemParametersInfoW(20, 0, fullpath, 0)

if __name__ == '__main__':

    # test_parse_url()

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
        # pprint.pprint(vars(ele))
        image_url = parse_url(ele.url)
        if image_url is not False:
            found = True
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