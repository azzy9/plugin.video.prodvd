import six
from six.moves import urllib_parse

from lib.constants import *

def build_url(query):

    """
    Helper function to build a Kodi xbmcgui.ListItem URL.
    :param query: Dictionary of url parameters to put in the URL.
    :returns: A formatted and urlencoded URL string.
    """

    return PLUGIN_URL + '?' + \
        urllib_parse.urlencode({k: v.encode('utf-8') if isinstance(v, six.text_type)
            else unicode(v, errors='ignore').encode('utf-8')
            for k, v in query.items()})
