from configparser import ConfigParser

from utils import (
    load_json_from_url,
    get_long_lived_token,
    set_logging,
    load_cli_args_and_config,
    print_token
)


def get_permanent_access_token_from_url(version, path, query):
    json_dict = load_json_from_url(version, path, query)
    return json_dict.get('data')[0].get('access_token')


def get_user_id_from_url(version, path, query):
    json_dict = load_json_from_url(version, path, query)
    return json_dict.get('id')


def get_permanent_user_token(version, app_id, app_secret, short_lived_token):
    long_lived_token = get_long_lived_token(version, app_id, app_secret, short_lived_token)

    user_id = get_user_id_from_url(
        version,
        '/me',
        {'access_token': long_lived_token}
    )

    return get_permanent_access_token_from_url(
        version,
        '/{}/accounts'.format(user_id),
        {'access_token': long_lived_token}
    )


def main():
    args = load_cli_args_and_config()
    set_logging(args.logging.upper())

    permanent_token = get_permanent_user_token(
        args.version, args.app_id, args.app_secret, args.short_lived_token
    )
    print_token('Page', permanent_token)


if __name__ == "__main__":
    main()
