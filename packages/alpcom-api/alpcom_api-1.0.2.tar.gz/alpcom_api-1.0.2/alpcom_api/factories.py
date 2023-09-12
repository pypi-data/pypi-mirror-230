from alpcom_api import apis, clients, cache


def get_public_api(url: str = None) -> apis.ALPPublicApi:
    cli = clients.ALPClient(url=url)
    return apis.ALPPublicApi(cli)


def get_private_api(key: str,
                    secret: str,
                    url: str = None,
                    token_cache: cache.TokenCache = None) -> apis.ALPPrivateApi:
    cli = clients.ALPAuthClient(
        key,
        secret,
        url=url,
        cache=token_cache
    )
    return apis.ALPPrivateApi(cli)
