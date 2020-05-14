import argparse
import logging
import json
from configparser import ConfigParser
from urllib.parse import urljoin, urlencode
from urllib.request import urlopen
from urllib.error import HTTPError


logger = logging.getLogger('fb_token')

BASE_URL = 'https://graph.facebook.com/{version}/'
LONG_LIVED_TOKEN_PATH = '/oauth/access_token'


def load_json_from_url(version, path, query_dict):
    base = BASE_URL.format(version=version)
    url = '{}?{}'.format(urljoin(base, path), urlencode(query_dict))
    logger.info('Requesting from url: {}'.format(url))

    try:
        return json.loads(urlopen(url).read())
    except HTTPError as e:
        logger.error(json.loads(e.read()))
        raise e


def get_long_lived_token(version, app_id, app_secret, short_lived_token):
    json_dict = load_json_from_url(
        version,
        '/oauth/access_token',
        {
            'grant_type': 'fb_exchange_token',
            'client_id': app_id,
            'client_secret': app_secret,
            'fb_exchange_token': short_lived_token,
        }
    )
    return json_dict.get('access_token')


def set_logging(level):
    # Set logging level based on user input. Default to Info
    numeric_level = getattr(logging, level, None)
    if not numeric_level:
        numeric_level = 20  # INFO
    logging.basicConfig(
        format='%(levelname)s -- %(filename)s:%(lineno)s -- %(message)s', level=numeric_level
    )


def print_token(type, token):
    print('\n{bold}Permanent {type} Token:{reset_all}\n{green}{token}{reset_all}'.format(
        bold='\033[1m',
        green='\033[32m',
        reset_all='\033[0m',
        type=type,
        token=token,
    ))


def load_cli_args_and_config(addl_args=[]):
    """
    `addl_args` should be a list of 2-tuples:
    [
        (('--page_id',), {'help': "Page ID.", 'required': True})
    ]
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('--version', help="FB API Version.", required=True)
    parser.add_argument('--app_id', help="App ID.", required=True)
    parser.add_argument('--app_secret', help="App Secret.", required=True)
    parser.add_argument('--short_lived_token', help="Short Lived Token.",  required=True)
    for args, kwargs in addl_args:
        # args should be a tuple, kwards should be a dict
        parser.add_argument(*args, **kwargs)
    parser.add_argument('-l', '--logging', help="Logging Level", default="")

    load_from_config_to_argparser(parser)

    return parser.parse_args()


def load_from_config_to_argparser(parser):

    config = ConfigParser()

    config.read('config.ini')
    main_config = config['main']

    parser.set_defaults(**{k: v for k, v in main_config.items()})
    # Reset `required` attribute when provided from config file
    for action in parser._actions:
        if action.required is True and main_config.get(action.dest):
            action.required = False