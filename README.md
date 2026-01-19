# Ralphs Booru

Ralphs Booru is a Python/Flask application I built to manage my enormous amount of memes I have collected. It is yet another booru with user capabilities, a tagging system and upcoming will be forums & pools!

## Get Started
- Clone the repository with `git clone https://github.com/ralphrbergman/ralphs-booru.git`
- Create a .env file and paste the following content:
```
# Directory where profile avatars get stored.
AVATAR_PATH=<path/to/user/avatars>
# Allow posting?
ALLOW_POSTS=true|false
# Allow user creation/logging in?
ALLOW_USERS=true|false

# All about leveling
# How many levels to level up
HARDNESS=5

MULTIPLIER=1
# From what level users can comment
COMMENT_LEVEL=0
# From what level users can post
POSTING_LEVEL=1
# From what level users can tag
TAGGING_LEVEL=1

# Path where post files are stored.
CONTENT_PATH=<path/to/media>
# Name of SQLite3 database file.
DATABASE_URI=sqlite:///<path-to-db>
# Name of Not Safe For Work tag. (Optional)
NSFW_TAG=nsfw
# Directories of sensitive (e.g NSFW) content.
SENSITIVE_DIRS=<directory-names-separated-by-comma>
# Path to temporary files, preferred it's in project's root.
# This directory stores thumbnails before they get moved.
TEMP_PATH=<path/to/temp>
# Secret key for authentication salting.
SECRET_KEY=abc
```
- Ensure all the mentioned directories exist before running!
- Symlink avatar.png in your avatars directory, or create your own, and make sure it's a PNG
- Create virtual environment & activate it
- Run `pip install -r requirements.txt`

## Running
To run web server, type in `flask run` within your terminal.
