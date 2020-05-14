from configparser import ConfigParser

from utils import (
    load_json_from_url,
    get_long_lived_token,
    set_logging,
    load_cli_args_and_config,
    print_token
)


def get_access_token_from_url(version, path, query):
    json_dict = load_json_from_url(version, path, query)
    return json_dict.get('access_token')


def get_permanent_page_token(version, page_id, app_id, app_secret, short_lived_token):
    long_lived_token = get_long_lived_token(version, app_id, app_secret, short_lived_token)

    return get_access_token_from_url(
        version,
        '/{}'.format(page_id),
        {
            'fields': 'access_token',
            'access_token': long_lived_token,
        }
    )


def main():
    args = load_cli_args_and_config([
        (('--page_id',), {'help': "Page ID.", 'required': True})
    ])
    print(args)

    set_logging(args.logging.upper())

    permanent_token = get_permanent_page_token(
        args.version, args.page_id, args.app_id, args.app_secret, args.short_lived_token
    )
    print_token('User', permanent_token)


if __name__ == "__main__":
    main()
