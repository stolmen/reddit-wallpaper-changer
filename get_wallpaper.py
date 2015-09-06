__author__ = 'ed'

# Imports
import praw
import pprint
import re
import ctypes
import urllib
import os
import argparse

# Constants
SUPPORTED_EXTENSIONS = (".jpg", ".png")
DEFAULT_EXTENSION = ".jpg"
GET_POST_LIMIT = 25
IMAGE_LOCATION = r"E:\pics\reddit_wallpaper_auto\\"
MODE_LIST = [
    'top',
    'hot',
    'new',
    'controversial'
]

# Some helper functions
def test_parse_url():
    """ Tests parse_url. """

    #print(parse_url(r"http://i.imgur.com/IC8Oa5T.png"))
    assert parse_url("http://imgur.com/asdf") == "http://imgur.com/asdf.jpg"
    assert parse_url("http://i.imgur.com/asdf") == "http://i.imgur.com/asdf.jpg"
    assert parse_url("penis") is False, 'Random shit test'
    assert parse_url("penis.jpg") is False, 'Incomplete URL test'
    assert parse_url("http://imgur.com/asdf.jpg") == "http://imgur.com/asdf.jpg"
    assert parse_url("http://i.imgur.com/asdf.jpg") == "http://i.imgur.com/asdf.jpg"
    assert parse_url("http://imgur.com/a/asdf") is False, 'Album test'
    assert parse_url("http://i.imgur.com/asdf.png") == "http://i.imgur.com/asdf.png"
    assert parse_url("http://i.imgur.com/asdf.blergh") is False, 'Unsupported extension test'


def parse_url(url):
    """ Determines whether the given url is valid for image extraction.
    If it is deemed to be worthy, then return a processed URL which
    points to the image file.
    """

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
    """ Given the fullpath to the image file, changes the wallpaper.
    This will work on Python 3.x, not 2.x. A slighly different method
    will have to be called if using Python 2.x.
    """
    ctypes.windll.user32.SystemParametersInfoW(20, 0, fullpath, 0)


def change_wallpaper_reddit(im_dir, subreddit, mode):
    """ Connects to reddit.com on the given subreddit and chooses an
    excellent wallpaper.
    """

    print(im_dir)
    print("The mode is {}".format(mode))
    # Connect to reddit
    user_agent = "Stolmen's Reddit Wallpaper grabber"
    print("Connecting to reddit")
    r = praw.Reddit(user_agent=user_agent)

    # Create subreddit
    the_subreddit = r.get_subreddit(subreddit_name=subreddit)

    # Retrieve the target post, from which to pull the image file.
    # Depends on the mode.
    assert mode in MODE_LIST, '{} is not in the allowed list of modes'.format(mode)
    if mode == 'new':
        the_post = the_subreddit.get_new(limit=GET_POST_LIMIT)
    elif mode == 'hot':
        the_post = the_subreddit.get_hot(limit=GET_POST_LIMIT)
    elif mode == 'top':
        the_post = the_subreddit.get_top_from_day(limit=GET_POST_LIMIT)
    elif mode == 'controversial':
        the_post = the_subreddit.get_controversial_from_day(limit=GET_POST_LIMIT)

    # Sift through the bucket of submissions, and find a suitable one
    found = False
    for ele in the_post:
        image_url = parse_url(ele.url)
        if image_url is not False:
            found = True
            # pprint.pprint(vars(ele))
            break

    # Download the image, and set it as the wallpaper.
    if found:
        image_filename = os.path.join(im_dir, image_url.split(r"/")[3])
        if not os.path.isfile(image_filename):
            print("Downloading %s..." % image_url)
            urllib.request.urlretrieve(image_url, image_filename)
        else:
            print("{} already exists! Not downloading after all..".format(image_filename))
    else:
        # In the unlikely event that no suitable URL is found,
        # throw some sort of error here.
        print("No suitable URL found. No wallpaper will be changed!")

    change_wallpaper(image_filename)


def main():
    # Parse arguments.
    parser = argparse.ArgumentParser(description='Reddit wallpaper changer.')
    parser.add_argument('-i', '--image_location', type=str, dest='image_location',
                        help='''Images will be downloaded to this location.
                            By default, this is the current working directory.''',
                        default=os.getcwd())
    parser.add_argument('-r', '--subreddit', type=str, dest='subreddit',
                        help='''The subreddit to pull images from. The default is
                        'wallpapers'. ''', default='wallpapers')
    parser.add_argument('-m', '--mode', type=str, dest='mode',
                        help=''' One of: (top, hot, new).
                        The default is 'new'. ''', default='new',
                        choices=MODE_LIST)
    args = parser.parse_args()

    test_parse_url()
    change_wallpaper_reddit(args.image_location, args.subreddit, args.mode)

if __name__ == '__main__':
    main()
