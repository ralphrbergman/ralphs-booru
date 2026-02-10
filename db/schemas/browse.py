from apiflask import Schema
from apiflask.fields import Integer, String

from api import DEFAULT_LIMIT, DEFAULT_SORT, DEFAULT_SORT_DIR, DEFAULT_TERMS

class BrowseIn(Schema):
    """ Represents inbound post browsing parameters object. """
    limit = Integer(load_default = DEFAULT_LIMIT)
    page = Integer(required = True)
    sort = String(load_default = DEFAULT_SORT)
    sort_by = String(load_default = DEFAULT_SORT_DIR)
    terms = String(load_default = DEFAULT_TERMS)
