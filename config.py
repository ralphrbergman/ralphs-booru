# Python module for storing environment variables in one place.

from os import getenv
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Project paths.
## Which directory stores user's avatar pictures
AVATAR_PATH = Path(getenv('AVATAR_PATH'))
## Which directory stores user uploaded content
CONTENT_PATH = Path(getenv('CONTENT_PATH'))
## Database connection URL
DATABASE_URI = getenv('DATABASE_URI')
## Which directory stores content temporarily
TEMP_PATH = Path(getenv('TEMP_PATH'))

# Control variables.
## Allow users to post content?
ALLOW_POSTS = getenv('ALLOW_POSTS') == 'true'
## Allow users to sign-up/login to accounts?
ALLOW_USERS = getenv('ALLOW_USERS') == 'true'
## Thumbnail dimensions for user uploaded content
TARGET_SIZE = getenv('TARGET_SIZE')

# Control variables for pagination.
## How many posts per page to display?
DEFAULT_LIMIT = int(getenv('DEFAULT_LIMIT'))
## Sorting column
DEFAULT_SORT = getenv('DEFAULT_SORT')
## Sorting direction
DEFAULT_SORT_DIR = getenv('DEFAULT_SORT_DIR')
## Posts per page maximum possible value
LIMIT_THRESHOLD = int(getenv('LIMIT_THRESHOLD'))

# Leveling variables.
## How many scores count as one level?
HARDNESS = int(getenv('HARDNESS'))
## Level multiplier
MULTIPLIER = int(getenv('MULTIPLIER'))
## From what level users can comment
COMMENT_LEVEL = int(getenv('COMMENT_LEVEL'))
## From what level users can post
POSTING_LEVEL = int(getenv('POSTING_LEVEL'))
## From what level users can tag other posts
TAGGING_LEVEL = int(getenv('TAGGING_LEVEL'))

# Miscellaneous variables.
## Not Safe For Work tag name
NSFW_TAG = getenv('NSFW_TAG')
## Cruptographic salt
SECRET_KEY = getenv('SECRET_KEY')
## Whether HTTPS is configured
SSL_ENABLED = getenv('SSL_ENABLED') == 'true'
## Comma separated list of directories that are marked NSFW
SENSITIVE_DIRS = getenv('SENSITIVE_DIRS').split(',')
SUPPORTED_TRANSLATIONS = ('en', 'lv')
