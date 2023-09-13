from . import utils
try:
    from StringIO import StringIO
except:
    from io import StringIO
import pandas as pd
import json, hashlib
from urllib.parse import quote
from seleya.utilities import api_base
from seleya.config.default_config import *
import pdb


def hash_code(input_string):
    md5_hash = hashlib.md5()
    md5_hash.update(input_string.encode('utf-8'))
    return md5_hash.hexdigest()


def feed(query,
         logic=["AND"],
         code=None,
         date_range='any',
         all_companies=0,
         pos=0,
         limit=10,
         lang='All'):

    http_client = api_base.__get_conn__()
    request_string = []

    request_string.append('api/esg/v3/feed/search')
    request_string.append('?query=')
    request_string.append(quote(json.dumps(query)))

    request_string.append('&logic=')
    request_string.append(quote(json.dumps(logic)))

    request_string.append('&date_range=')
    request_string.append(str(date_range))

    request_string.append('&code=')
    request_string.append(str(hash_code(code)))

    request_string.append('&all_companies=')
    request_string.append(str(all_companies))

    request_string.append('&page=')
    request_string.append(str(pos + 1))

    request_string.append('&limit=')
    request_string.append(str(limit))

    request_string.append('&lang=')
    request_string.append(str(lang))

    result = api_base.__get_result__('GET',
                                     ''.join(request_string),
                                     http_client,
                                     gw=True)
    return result if format == 'json' else pd.DataFrame(
        json.loads(result)['data']['data'])
