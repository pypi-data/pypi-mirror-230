import re
from sqlalchemy.engine.url import make_url

GROUP_DELIMITER = re.compile(r"\s*\,\s*")
KEY_VALUE_DELIMITER = re.compile(r"\s*\:\s*")


def parse_boolean(bool_string):
    bool_string = bool_string.lower()
    if bool_string == "true":
        return True
    elif bool_string == "false":
        return False
    else:
        raise ValueError()


def parse_url(origin_url):
    url = make_url(origin_url)
    query = dict(url.query)

    instance = url.host.split('.')[0]
    length = len(instance) + 1
    protocol = None
    service = None
    if 'protocol' in query:
        protocol = query.pop('protocol')
        if protocol == 'http':
            if not url.host[length:].endswith(':80'):
                service = 'http://' + url.host[length:] + ':80'
            else:
                service = 'http://' + url.host[length:]
        else:
            raise ValueError('protocol parameter must be http. Other protocols are not supported yet.')
    else:
        protocol = 'https'
        service = 'https://' + url.host[length:] + ':443' if not url.host[length:].endswith(':443') else 'https://' + url.host[length:]

    workspace = url.database
    username = url.username
    driver_name = url.drivername
    password = url.password
    schema = None
    magic_token = None

    if 'virtualcluster' in query or 'virtualCluster' in query or 'vcluster' in query:
        if 'virtualcluster' in query:
            vcluster = query.pop('virtualcluster')
        elif 'virtualCluster' in query:
            vcluster = query.pop('virtualCluster')
        else:
            vcluster = query.pop('vcluster')
    else:
        raise ValueError('url must have `virtualcluster` or `virtualCluster` or `vcluster` parameter.')

    if 'schema' in query:
        schema = query.pop('schema')

    if 'magic_token' in query:
        magic_token = query.pop('magic_token')

    return (
        service,
        username,
        driver_name,
        password,
        instance,
        workspace,
        vcluster,
        schema,
        magic_token,
        protocol,
    )
